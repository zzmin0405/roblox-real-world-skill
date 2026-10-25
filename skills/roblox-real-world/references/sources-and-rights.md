# 자료 선택과 이용 조건

2026-10-25에 확인한 공식 자료의 출발점이다. 새 데이터를 취득하거나 배포할 때 **선택한 배포본의 현재 조건**을 확인한다. 아래 링크는 일괄 이용 허가가 아니다. 이 스킬의 MIT 라이선스가 외부 데이터에 적용되지 않는다.

## 기존 공개 도구

아래는 README·코드·라이선스를 확인한 후보이며 이 스킬의 필수 의존성이 아니다. 독립적인 Studio 실행·실경 대조·모바일 성능 검증은 수행하지 않았다. 새 도구가 필요할 때 현재 버전·라이선스·외부 데이터 조건·설치 스크립트를 확인하고, 기존 맵과 분리한 작은 범위에서 결과를 검증한 뒤 적용한다.

| 프로젝트 | 활용할 수 있는 부분 | 채택 전 확인 |
|---|---|---|
| [WorldLoader](https://github.com/Klingaac/WorldLoader-Roblox-Plugin) · MIT | Studio 플러그인에서 OSM·고도 기반 지형·건물·도로·철도 제작 | `EditableModules/WayProperties.lua`에 기본 건물 높이·색·재질 규칙이 있다. 측량·현장 입면의 대체로 삼지 않는다. |
| [Arnis Roblox](https://github.com/adpena/arnis-roblox) · Apache-2.0 | Rust compiler의 OSM·DEM·위성 자료 → manifest → Roblox runtime 경로 | 직접 빌드·VertigoSync가 필요하다. 절차적 입면과 높이장은 실측 입면·교량 아래를 보장하지 않는다. 현재 bootstrap의 Studio 자동 열기는 Windows 경로를 제공하지 않으므로 place를 수동으로 열 수 있는지 확인한다. |
| [The World, 1:1 Scale](https://github.com/biotoxin495/roblox-the-world-1to1-scale_osm-viewer) · MIT | 위치 선택·Overpass 요청·지도 렌더링을 배우는 실행 예제 | 저자가 미니멀한 표현을 목표로 명시한다. 공용 Overpass의 지연·제한이 있어 고트래픽 운영 경로는 별도 설계한다. |

범용 [Roblox-Skills](https://github.com/justOzy/Roblox-Skills)에는 Luau·UI·성능 등 스킬이 있지만 실경 정합·입면·보행 대조 전용은 확인하지 못했다. [ATTRIBUTION.md](https://github.com/justOzy/Roblox-Skills/blob/main/ATTRIBUTION.md)는 일부 원본 스킬의 라이선스 부재를 명시한다. 또한 현재 `roblox-performance`의 `workspace.StreamingEnabled` 대입과 `workspace:RequestStreamAroundAsync` 예시는 공식 API와 맞지 않는다. [Streaming 설정은 Studio에서 지정](https://create.roblox.com/docs/workspace/streaming)하고, 요청 메서드는 [Player](https://create.roblox.com/docs/reference/engine/classes/Player#RequestStreamAroundAsync)에 속한다. 모음을 통째로 설치·재배포하지 말고 필요한 내용과 원본 조건을 개별 검토한다.

## 제작 결정을 위한 자료 선택

먼저 같은 구간의 허용된 지상·항공·실측 자료를 조합한다. 자체 촬영 사진·영상은 좋은 후보지만 촬영 허용 범위와 포함된 타인·저작물 등의 권리는 별도로 확인한다. 공개 360도나 무료 다운로드라는 사실만으로 모델링·텍스처·재배포 가능 여부를 확정하지 않는다.

일본 이외의 지역에서도 해당 국가·지방정부의 건물 윤곽, 정사영상, LiDAR, DEM, 공개 도시 모델을 같은 방식으로 평가한다. 자료가 없으면 현장 측정·허용된 사진측량·개별 모델링으로 보완한다. 임의 형상을 실제 측량으로 표시하지 않는다.

| 공급자 | 활용과 확인할 조건 | 공식 출처 |
|---|---|---|
| PLATEAU | 도시·연도·LOD·지물 분류·사진/텍스처를 확인한다. 사이트 기본 정책과 개별 배포본의 라이선스가 다를 수 있다. CC BY로 일괄 간주하지 않는다. | [사이트 정책](https://www.mlit.go.jp/plateau/site-policy/), [FAQ](https://www.mlit.go.jp/plateau/faq/) |
| 일본 국토지리원 GSI | DEM·항공·측량 자료의 관측 시점·정밀도·표고 기준을 확인한다. 출처·가공 표시와 제3자 자료/권리, 해당 자료의 추가 조건을 확인한다. | [콘텐츠 이용규약](https://www.gsi.go.jp/kikakuchousei/kikakuchousei40182.html) |
| OpenStreetMap | 도로·윤곽의 위치·태그·관측 시기를 평가한다. ODbL의 기여자 표시, 파생 데이터베이스와 최종 표현물에 대한 조건을 구분한다. MIT 코드와 OSM 데이터의 조건을 분리한다. | [저작권](https://www.openstreetmap.org/copyright), [표현물 지침](https://osmfoundation.org/wiki/Licence/Community_Guidelines/Produced_Work_-_Guideline) |
| 자체/허용된 사진·스캔 | 입면·문턱·재질을 보완한다. 제작·가공·공개 업로드·재배포에 필요한 권리와 촬영 조건을 원본별로 기록한다. | 해당 촬영/배포본의 원본 및 이용 조건 |

## Google 자료를 다룰 때

[Google Geo Guidelines](https://about.google/brand-resource-center/products-and-services/geo-guidelines/)와 해당 [Maps Platform 약관](https://cloud.google.com/maps-platform/terms)을 확인한다. Street View 이미지의 스크린샷·분리 다운로드·이어붙이기·정보 추출/디지타이징, Google Earth 출력에서의 3D 재구성 등에는 제한이 있다. 출처를 적는 것만으로 허용되지 않는다.

Google 링크를 받았으면 위치 식별에 활용하되 그 화면을 추출해 텍스처·데이터셋·공개 저장소로 옮기거나 모델 제작에 사용할 권한이 있다고 간주하지 않는다. 해당 용도를 허용하는 별도 권한이 확인되지 않으면 자체 촬영·공개 측량·이용 허용 사진 등 대체 근거로 제작한다. 사용자 360도 사진도 서비스 화면의 표시 권한과 원본 사진 이용 권한을 구분한다.

## 기록과 공개 범위

프로젝트의 기존 기록에 다음 정보를 모은다. 이미 동일한 정보가 있으면 복제하지 않고 참조한다.

- 원본 URL·자료 ID·공급자·촬영자, 다운로드/확인일과 실제 촬영/측량일.
- 대상 범위·카메라 위치/방향, CRS·축 순서·단위·수직 기준, 정밀도/해상도·LOD와 가려진 영역.
- 실제 필요한 용도: 열람, 분석·파생 모델, 텍스처, Roblox 업로드, 공개 재배포. 허용·금지·미확정을 용도별로 구분.
- 원본 라이선스·표시 문구·가공 사실·제3자 예외와 공개할 파일의 범위.

제작 지침·코드와 원본 데이터·가공 메시·사진·플레이 화면의 배포 조건은 따로 판단한다. 공개 권한이 없는 자료는 링크·취득 방법만 제공할 수 있는지 확인하고 파일을 포함하지 않는다. 실측 좌표·관측 기록에 사적인 위치나 식별 가능한 개인 정보가 섞이면 필요한 범위만 공개한다.

## Roblox의 현재 기술 문서

플랫폼 제약과 가져오기 기능이 변할 수 있으므로 새 제작 방식의 최초 에셋에서 현재 문서를 확인한다. 같은 설정·자료가 유지되는 반복 수정마다 다시 조사하지 않는다.

- [단위](https://create.roblox.com/docs/physics/units): 표준 stud와 물리 단위. 프로젝트의 실제 import 크기는 별도 확인한다.
- [Importer](https://create.roblox.com/docs/studio/importer), [메시 규격](https://create.roblox.com/docs/art/modeling/specifications): 지원 형식·축·크기·소유/사용 권한·현재 제한.
- [Streaming](https://create.roblox.com/docs/workspace/streaming): 큰 맵의 로딩과 인스턴스 생명주기.
- [성능 개선](https://create.roblox.com/docs/performance-optimization/improve), [실기기 테스트](https://create.roblox.com/docs/performance-optimization/test-on-hardware): 에셋 재사용, 병목 측정과 대상 기기의 검증.

데이터 제공자의 정확도나 Roblox의 기술적 가져오기 성공이 보행 외관의 일치를 증명하지 않는다. 최종 판단은 권리가 허용된 실경과 현재 Play를 같은 시점에서 대조한다.
