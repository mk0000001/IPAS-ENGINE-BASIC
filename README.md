# IPAS-ENGINE-BASIC

G-code 주석 메타데이터와 단순 비용 산술을 살펴보는 공개 학습용 스타터입니다.
운영용 IPAS 엔진을 제공하거나 대체하지 않습니다. 초기의 기본 개념만 작은 예제로
새로 작성했으며, 운영 엔진 소스와 Git 이력을 포함하지 않습니다.

Python 3.10 이상과 표준 라이브러리만 사용합니다. 저장소 루트에서 실행합니다.

```console
python -B -m unittest discover -s tests -v
python -B -m examples.basic_usage
```

`ipas_gcode_basic.read_header(binary_stream)`은 처음 나오는 명령 앞의 주석만 읽습니다.
다음 네 가지 형식을 지원합니다.

```gcode
;TIME:3600
; estimated printing time (normal mode) = 1h 0m 0s
; filament used [g] = 12.5
; filament_type = PLA; PETG
```

시간은 초 단위 정수 또는 순서대로 나열한 `d h m s` 정수입니다. 질량은 하나의
0 이상 고정소수점 수입니다. 소재명은 선언된 문자열이며 실제 사용 도구와 연결하지
않습니다. 값이 없으면 `None` 또는 빈 튜플을 반환합니다. 서로 다른 중복 값은 오류입니다.
헤더는 64 KiB, 한 줄은 줄바꿈 포함 4096 바이트로 제한하며 UTF-8 텍스트만 받습니다.
명령 뒤의 주석과 파일 끝의 메타데이터는 읽지 않습니다. 선언된 값의 정확성을 보증하지 않습니다.

`ipas_cost_basic.illustrative_cost(seconds, grams, hourly_rate, material_rate_per_gram)`은
호출자가 입력한 네 값으로 `seconds / 3600 * hourly_rate + grams * material_rate_per_gram`을
계산합니다. 입력은 0 이상 고정소수점 문자열 또는 정수이며, 각 값은 10억 이하,
소수부는 9자리 이하입니다. 반환값은 `Decimal`이고 40자리 십진 연산을 사용합니다.
통화와 청구 반올림 규칙은 정하지 않습니다. 예제 요율은 설명을 위한 임의의 숫자입니다.

이 스타터에는 이동 경로·압출량 추론, 3MF 처리, 강도 평가, 자동 판정,
운영 요금 정책, 서비스 연결 또는 배포 설정이 없습니다.

---

This is a small public teaching starter for declared G-code comment metadata and
illustrative cost arithmetic. It is independently written around elementary
starting concepts. It contains no production engine source or inherited Git history.

Use Python 3.10 or newer. No third-party packages are required. Run the commands
above from the repository root. The example G-code is synthetic.

`read_header(binary_stream)` reads only leading comments, stopping at the first
command. It recognizes exactly the four illustrated comment formats. Time is an
integer number of seconds or integer `d h m s` units in that order. Filament mass
is one nonnegative fixed-point number. Material labels remain declared labels;
they do not identify active tools. Missing values remain unknown. Conflicting
duplicates and malformed recognized values raise `ValueError`.

The header is limited to 64 KiB and each line to 4096 bytes including its newline.
Input must be UTF-8 text. Comments after the first command, including footer
metadata, are outside its scope. Declarations are unverified.

`illustrative_cost` calculates only the formula shown above, with four explicit
caller-supplied inputs. Inputs are nonnegative fixed-point strings or integers,
at most one billion each and at most nine fractional digits. The result is a
`Decimal` calculated with 40 significant digits. Currency and billing rounding
are unspecified; the sample rates are arbitrary teaching values.

There is no toolpath or extrusion inference, archive handling, strength analysis,
automatic assessment, production pricing policy, service integration, or deployment
configuration in this starter. `PUBLIC_FILES.json` records the intended public
file allowlist and hashes of its content files; it is a scope record, not a signature.
