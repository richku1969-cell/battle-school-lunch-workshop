from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class McpError(Exception):
    code: str
    message: str
    retryable: bool = False

    def to_payload(self) -> dict[str, object]:
        return {"ok": False, "code": self.code, "message": self.message, "retryable": self.retryable}


def empty_query_error() -> McpError:
    return McpError(code="EMPTY_QUERY", message="학교 검색어를 입력해 주세요.")


def missing_field_error(field_name: str) -> McpError:
    return McpError(code="MISSING_FIELD", message=f"필수 입력값이 누락되었습니다: {field_name}")


def invalid_date_error(field_name: str) -> McpError:
    return McpError(code="INVALID_DATE", message=f"유효하지 않은 날짜입니다: {field_name}")


def invalid_date_range_error() -> McpError:
    return McpError(code="INVALID_DATE_RANGE", message="시작일은 종료일보다 늦을 수 없습니다.")


def date_range_too_large_error(max_days: int) -> McpError:
    return McpError(code="DATE_RANGE_TOO_LARGE", message=f"조회 기간은 최대 {max_days}일까지만 가능합니다.")


def no_schools_found_error() -> McpError:
    return McpError(code="NO_SCHOOLS_FOUND", message="일치하는 학교를 찾을 수 없습니다.")


def no_meals_found_error() -> McpError:
    return McpError(code="NO_MEALS_FOUND", message="선택한 기간에 중식 정보가 없습니다.")


def neis_unauthorized_error() -> McpError:
    return McpError(code="NEIS_UNAUTHORIZED", message="현재 급식 서비스를 조회할 수 없습니다.")


def neis_invalid_response_error() -> McpError:
    return McpError(code="NEIS_INVALID_RESPONSE", message="외부 급식 서비스 응답을 처리할 수 없습니다.")


def neis_timeout_error() -> McpError:
    return McpError(code="NEIS_TIMEOUT", message="급식 서비스 응답이 지연되고 있습니다.", retryable=True)


def neis_rate_limited_error() -> McpError:
    return McpError(code="NEIS_RATE_LIMITED", message="요청이 많아 잠시 후 다시 시도해 주세요.", retryable=True)
