# Roblox Real World Skill

현실의 거리·도시·관광지를 Roblox에서 **실제로 걸을 때 닮게** 만드는 한국어 Codex 스킬입니다.

재현도는 건물을 많이 가져온 것보다 도로 폭, 연속 건물 배치, 지면 단차, 주요 실루엣, 보행 카메라에서의 시선과 연결에 달려 있습니다. 이 스킬은 자료 확보 → 좌표 정합 → Studio 제작 → 같은 시점의 실제 Play 비교를 한 작업으로 연결합니다.

## 거의 똑같이 느끼려면

1. 재현할 거리의 시작·끝과 시기를 정하고, 같은 범위의 사용 가능한 지상 사진·항공영상·실측 데이터를 확보합니다.
2. 좌표·축척·표고를 맞춰 도로·보도·주요 건물·강·다리의 연결부터 제작합니다.
3. 실제 아바타로 걸으며 실경과 같은 카메라에서 비교합니다. 큰 배치·지면 오류를 먼저 고칩니다.
4. 검증한 구간에 근접 입면·처마·재질·안내·환경음을 완성하고, 대상 휴대폰에서 비용을 조절합니다.

도시 모델과 항공사진은 좋은 출발점이지만 가까이서 보는 입구·교각·난간·벽 재질까지 보장하지 않습니다. 필요한 면은 허용된 사진이나 개별 모델링으로 보완해야 합니다. 스킬은 이 판단을 재사용하는 지침이며, 장소를 한 번에 복제하는 엔진이나 재현도 보증서는 아닙니다.

## 포함된 것

- [스킬 지침](skills/roblox-real-world/SKILL.md): 전체 제작과 부분 수정, 가장 큰 차이 우선, 실제 관찰 후 채택.
- [공간 구성](skills/roblox-real-world/references/spatial-and-studio.md): 좌표·표고·지면·Studio·모바일 비용.
- [자료와 이용 조건](skills/roblox-real-world/references/sources-and-rights.md): 공식 자료 연결과 제작/배포 권한 구분.
- 수평 정합 도우미: 미터 투영좌표와 Roblox X/Z의 대응으로 이동·회전·축척과 잔차를 계산하는 Python CLI.
- 합성 예시와 자동 테스트: 실제 지도·사진·게임 원본을 포함하지 않습니다.

## 이미 있는 도구와의 관계

현실 지도에서 Roblox 맵을 생성하는 공개 구현은 이미 있습니다. 이 스킬은 기존 importer를 평가·활용하면서 좌표·높이·지상 입면·보행 검수를 연결하는 역할입니다.

| 프로젝트 | 기존 기능 | 이 스킬에서 보완하는 판단 |
|---|---|---|
| [WorldLoader](https://github.com/Klingaac/WorldLoader-Roblox-Plugin) · MIT | Studio 플러그인으로 OSM·고도 기반 맵 생성 | 기본 높이·색·재질과 현장 형상을 구분하고 실제 보행 시점을 대조 |
| [Arnis Roblox](https://github.com/adpena/arnis-roblox) · Apache-2.0 | Rust·manifest·Roblox runtime으로 도시 생성 | 절차적 입면·DEM의 표현 한계, 기존 프로젝트 축척·소유 범위 확인 |
| [The World, 1:1 Scale](https://github.com/biotoxin495/roblox-the-world-1to1-scale_osm-viewer) · MIT | 세계 위치 선택과 OSM 기반 탐색 예제 | 미니멀한 지도 표현과 실경 재현 목표를 구분 |

2026-10-25 기준 README·소스·라이선스를 확인했습니다. 이 저장소에서 위 도구를 실행하거나 외관·모바일 성능을 통과시킨 것은 아닙니다. [선택 시 주의점과 범용 스킬 검토](skills/roblox-real-world/references/sources-and-rights.md#기존-공개-도구)

## 설치

`skills/roblox-real-world` 폴더 전체가 설치 단위입니다. 특정 Roblox 프로젝트에서 사용하려면 그 프로젝트 루트에서 다음과 같이 복사합니다. 같은 이름의 기존 스킬이 있다면 내용을 검토한 뒤 교체하세요.

PowerShell:

```powershell
git clone https://github.com/zzmin0405/roblox-real-world-skill.git
New-Item -ItemType Directory -Force '.agents/skills' | Out-Null
Copy-Item -LiteralPath 'roblox-real-world-skill/skills/roblox-real-world' -Destination '.agents/skills/roblox-real-world' -Recurse
```

macOS/Linux:

```sh
git clone https://github.com/zzmin0405/roblox-real-world-skill.git
mkdir -p .agents/skills
cp -R roblox-real-world-skill/skills/roblox-real-world .agents/skills/roblox-real-world
```

여러 프로젝트에서 쓰려면 복사 목적지를 `~/.agents/skills/roblox-real-world`로 바꿉니다. 설치 경로·인식 방식은 사용하는 호스트의 설정을 따릅니다. [OpenAI 공식 스킬 문서](https://learn.chatgpt.com/docs/build-skills)

## 사용

Codex에서 스킬을 명시적으로 호출하거나 실제 장소 재현 요청을 합니다.

```text
$roblox-real-world
교토 기온시조역부터 가와라마치역까지 실제 산책처럼 느껴지는 맵을 만들고 싶어.
지금 프로젝트의 자료와 Play부터 확인하고 가장 큰 차이를 고쳐줘.
기존 제작 범위를 유지하고 휴대폰에서 걸을 수 있게 해줘.
```

```text
$roblox-real-world
현재 맵은 다리 아래가 비고 강변이 흙언덕처럼 보여.
같은 보행 카메라에서 원인을 확인하고 연결된 지면과 호안을 고쳐줘.
```

Studio에서 실제로 수정하고 Play를 검수하려면 Studio와 사용 가능한 제어 도구가 필요합니다. 연결된 공식 Studio 도구를 우선 사용하며, 특정 MCP 서버 설치를 강제하지 않습니다. Blender·GIS 도구는 필요한 개별 작업에 사용합니다. 다른 품질 스킬이나 이 저장소 밖의 프로젝트 문서는 필수 의존성이 아닙니다.

## 좌표 정합 도우미

Python 3.10 이상, 외부 패키지 없음. 저장소 루트에서 실행합니다.

```sh
python skills/roblox-real-world/scripts/fit_local_frame.py skills/roblox-real-world/assets/control-points.synthetic.json --max-error-studs 0.01
python -m unittest discover -s tests -v
```

위경도를 미터로 변환하거나 표고를 보정하는 도구가 아닙니다. 비공선 기준점 3개 이상을 사용하고, 입력 CRS의 축·단위를 먼저 맞추세요. 잔차가 작아도 실제 장면의 외관과 보행 검증은 별개입니다. [입력 형식과 종료 코드](skills/roblox-real-world/references/spatial-and-studio.md#수평-정합-도우미)

## 검증 범위

스킬 메타데이터와 좌표 도구의 동작을 검사할 수 있습니다. 이 저장소 자체가 특정 장소의 실경 외관, 오디오 청취, 모바일 성능을 통과했다는 뜻은 아닙니다. 실제 제작 결과는 최신 소스·실행 파일·현재 Play와 연결해 별도로 확인해야 합니다.

## 기여와 라이선스

재현 가능한 입력, 기대한 결과, 실제 결과를 이슈나 PR에 적어 주세요. 문서·PR·커밋 메시지는 한국어로 작성합니다. 실제 사진·도시 데이터를 기여할 때는 원본별 라이선스와 재배포 조건을 함께 제시하세요. API 키·쿠키·사적인 위치 기록은 포함하지 마세요.

스킬 지침과 코드는 [MIT 라이선스](LICENSE)입니다. `LICENSE`는 표준 MIT 영문 원문을 유지합니다. 외부 지도·사진·측량·도시 모델의 권리는 각각의 원본 조건을 따르며 이 저장소의 MIT로 바뀌지 않습니다. Roblox·OpenAI 또는 자료 공급자의 공식 제품이나 제휴 프로젝트가 아닙니다.
