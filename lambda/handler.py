import json
import os
import time
import uuid
from datetime import datetime, timezone

import boto3
from botocore.exceptions import BotoCoreError, ClientError

# -------- Helpers --------

class BadRequest(Exception):
    """Raised when input validation fails."""
    def __init__(self, message, details=None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

def _response(status_code: int, body: dict):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }

def _emit_emf_metrics(metric_name: str, value: float, dimensions: dict | None = None):
    """
    Emit CloudWatch Embedded Metric Format (EMF) to stdout.
    CloudWatch Logs will automatically parse and create metrics.
    """
    dims = dimensions or {}
    emf = {
        "_aws": {
            "Timestamp": int(time.time() * 1000),
            "CloudWatchMetrics": [
                {
                    "Namespace": "CloudTranslateProject",
                    "Dimensions": [list(dims.keys())] if dims else [[]],
                    "Metrics": [{"Name": metric_name, "Unit": "Count"}],
                }
            ],
        },
        metric_name: value,
    }
    emf.update(dims)
    print(json.dumps(emf))  # EMF must be on a single line

def _validate_event(event):
    """
    Accepts either API Gateway HTTP API (payload v2) or raw dict.
    Expected JSON body:
      {
        "source_lang": "en",
        "target_lang": "fr",
        "texts": ["Hello", "How are you?"]
      }
    """
    # API Gateway HTTP API v2 event?
    if isinstance(event, dict) and "body" in event:
        try:
            body = json.loads(event["body"] or "{}")
        except json.JSONDecodeError:
            raise BadRequest("Request body must be valid JSON.")
    else:
        body = event if isinstance(event, dict) else {}

    source_lang = body.get("source_lang")
    target_lang = body.get("target_lang")
    texts = body.get("texts")

    # Basic checks (don’t hardcode full language list; let Translate validate)
    if not isinstance(source_lang, str) or not source_lang.strip():
        raise BadRequest("source_lang is required and must be a non-empty string.")
    if not isinstance(target_lang, str) or not target_lang.strip():
        raise BadRequest("target_lang is required and must be a non-empty string.")
    if source_lang.strip().lower() == target_lang.strip().lower():
        raise BadRequest("source_lang and target_lang cannot be the same.")
    if not isinstance(texts, list) or len(texts) == 0:
        raise BadRequest("texts must be a non-empty array of strings.")
    if any((not isinstance(t, str) or not t.strip()) for t in texts):
        raise BadRequest("All items in texts must be non-empty strings.")

    # Optional guardrail to avoid long invocations
    if len(texts) > 100:
        raise BadRequest("texts length exceeds limit (max 100).")

    return {
        "source_lang": source_lang.strip(),
        "target_lang": target_lang.strip(),
        "texts": [t.strip() for t in texts],
        "raw_body": body,
    }

def _s3_put_json(bucket: str, key: str, obj: dict):
    s3 = boto3.client("s3")
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(obj, ensure_ascii=False).encode("utf-8"),
        ContentType="application/json",
        ServerSideEncryption="AES256",
    )

# -------- Handler --------

def lambda_handler(event, context):
    start = time.time()
    req_id = getattr(context, "aws_request_id", str(uuid.uuid4()))

    try:
        REQUESTS_BUCKET = os.environ.get("REQUESTS_BUCKET")
        RESPONSES_BUCKET = os.environ.get("RESPONSES_BUCKET")
        AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
        
        if not REQUESTS_BUCKET or not RESPONSES_BUCKET:
            raise RuntimeError("Missing env vars: REQUESTS_BUCKET/RESPONSES_BUCKET.")

        parsed = _validate_event(event)
        job_id = str(uuid.uuid4())

        # Keys
        date_prefix = datetime.now(timezone.utc).strftime("%Y/%m/%d")
        req_key = f"requests/{date_prefix}/{job_id}/request.json"
        out_key = f"responses/{date_prefix}/{job_id}/result.json"

        # Store raw request
        _s3_put_json(
            REQUESTS_BUCKET,
            req_key,
            {
                "jobId": job_id,
                "request": parsed["raw_body"],
                "receivedAt": datetime.now(timezone.utc).isoformat(),
                "region": AWS_REGION,
                "awsRequestId": req_id,
            },
        )

        # Translate each sentence
        translate = boto3.client("translate")
        translations = []
        for text in parsed["texts"]:
            # Amazon Translate API call
            resp = translate.translate_text(
                Text=text,
                SourceLanguageCode=parsed["source_lang"],
                TargetLanguageCode=parsed["target_lang"],
            )
            translations.append(
                {
                    "source": text,
                    "translated": resp.get("TranslatedText"),
                    "sourceLang": resp.get("SourceLanguageCode"),
                    "targetLang": resp.get("TargetLanguageCode"),
                }
            )

        # Build output payload
        output = {
            "jobId": job_id,
            "source_lang": parsed["source_lang"],
            "target_lang": parsed["target_lang"],
            "count": len(translations),
            "items": translations,
            "completedAt": datetime.now(timezone.utc).isoformat(),
        }

        # Store result
        _s3_put_json(RESPONSES_BUCKET, out_key, output)

        duration_ms = int((time.time() - start) * 1000)
        _emit_emf_metrics("Requests", 1, {"Stage": os.environ.get("ENV", "dev")})
        _emit_emf_metrics("Success", 1, {"Stage": os.environ.get("ENV", "dev")})
        _emit_emf_metrics("DurationMs", duration_ms, {"Stage": os.environ.get("ENV", "dev")})

        # HTTP 200 response to client with translation results
        return _response(
            200,
            {
                "jobId": job_id,
                "outputKey": out_key,
                "responsesBucket": RESPONSES_BUCKET,
                "translations": translations,  # Include actual translations
                "source_lang": parsed["source_lang"],
                "target_lang": parsed["target_lang"],
                "count": len(translations)
            },
        )

    except BadRequest as e:
        _emit_emf_metrics("BadRequest", 1, {"Stage": os.environ.get("ENV", "dev")})
        return _response(400, {"error": "BadRequest", "message": e.message, "details": e.details or {}})

    except (ClientError, BotoCoreError) as e:
        # Likely AWS service error (Translate/S3)
        _emit_emf_metrics("AwsError", 1, {"Stage": os.environ.get("ENV", "dev")})
        return _response(502, {"error": "AwsError", "message": str(e)})

    except Exception as e:
        _emit_emf_metrics("UnhandledError", 1, {"Stage": os.environ.get("ENV", "dev")})
        return _response(500, {"error": "InternalServerError", "message": str(e)})
