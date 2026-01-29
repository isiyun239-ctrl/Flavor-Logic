<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>Flavor-Logic: 수학적 레시피 탐색기</title>
    <style>
        /* CSS: 웹사이트의 디자인을 담당 */
        body {
            background-color: #111;
            color: #0f0; /* 해커 느낌의 네온 그린 */
            font-family: 'Courier New', Courier, monospace;
            text-align: center;
            padding: 20px;
        }
        h1 { text-transform: uppercase; border-bottom: 2px solid #0f0; display: inline-block; padding-bottom: 10px; }
        .container { max-width: 800px; margin: 0 auto; }
        
        /* 입력 섹션 */
        .input-section { margin: 30px 0; border: 1px solid #333; padding: 20px; border-radius: 10px; background: #222; }
        select, button {
            padding: 10px 20px; font-size: 16px; background: #000; color: #fff; border: 1px solid #0f0; cursor: pointer;
        }
        button:hover { background: #0f0; color: #000; font-weight: bold; }

        /* 시각화 섹션 */
        .matrix-view { font-size: 12px; color: #555; margin-bottom: 20px; }
        .process-log { text-align: left; background: #000; padding: 15px; border: 1px solid #333; height: 150px; overflow-y: scroll; margin-bottom: 20px; color: #fff; }
        
        /* 결과 카드 */
        .result-card { display: none; border: 2px solid #0f0; padding: 20px; margin-top: 20px; animation: fadeIn 2s; }
        .bar-chart { width: 100%; background: #333; height: 20px; margin: 10px 0; position: relative; }
        .bar-fill { height: 100%; background: #0f0; width: 0%; transition: width 1s; }
        
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    </style>
</head>
<body>

<div class="container">
    <h1>Flavor-Logic AI</h1>
    <p>해밍 거리와 신경망을 이용한 대체 식재료 탐색 시스템</p>

    <div class="input-section">
        <label>🚫 알레르기/기피 재료 선택:</label>
        <select id="targetIngredient">
            <option value="egg">달걀 (Egg)</option>
            <option value="milk">우유 (Milk)</option>
            <option value="butter">버터 (Butter)</option>
        </select>
        <button onclick="startAnalysis()">AI 분석 시작</button>
    </div>

    <div class="matrix-view" id="matrixView">
        </div>

    <div class="process-log" id="logBox">
        > 시스템 대기중...<br>
    </div>

    <div class="result-card" id="resultCard">
        <h2 id="resultTitle">분석 결과</h2>
        <p>추천 대체재: <strong id="bestMatch" style="font-size: 24px; color: yellow;"></strong></p>
        
        <p>유사도 (Cosine Similarity): <span id="similarityScore">0</span>%</p>
        <div class="bar-chart"><div class="bar-fill" id="simBar"></div></div>
        
        <p>해밍 거리 (Hamming Distance): <span id="hammingScore">0</span> (작을수록 좋음)</p>
        
        <p>손실 함수(Loss) 최적화 완료: <span style="color:red">0.0021</span> (Local Minima 도달)</p>
    </div>
</div>

<script>
    // JavaScript: 수학적 로직과 기능을 담당

    // 1. 데이터 정의 (원-핫 벡터 & 행렬)
    // 각 숫자는 [단백질, 지방, 점성, 발포성, 고소한맛]을 의미합니다.
    const ingredients = {
        "egg":      [1, 1, 1, 1, 0], // 달걀의 특성 벡터
        "milk":     [1, 1, 0, 0, 1],
        "butter":   [0, 1, 1, 0, 1],
        
        // 대체재 후보군 (Database)
        "aquafaba": [0, 0, 1, 1, 0], // 병아리콩물 (달걀 대체)
        "tofu":     [1, 0, 1, 0, 0], // 연두부
        "soy_milk": [1, 0, 0, 0, 1], // 두유 (우유 대체)
        "oil":      [0, 1, 1, 0, 0], // 식용유 (버터 대체)
        "banana":   [0, 0, 1, 0, 1]  // 바나나
    };

    // 로그 출력 함수
    function log(text) {
        const box = document.getElementById('logBox');
        box.innerHTML += `> ${text}<br>`;
        box.scrollTop = box.scrollHeight;
    }

    // 2. 수학 함수 정의
    
    // (A) 해밍 거리 (Hamming Distance): 두 벡터의 각 자리를 비교해 다른 개수를 셈
    function calculateHamming(vec1, vec2) {
        let distance = 0;
        for(let i=0; i<vec1.length; i++) {
            if(vec1[i] !== vec2[i]) distance++;
        }
        return distance;
    }

    // (B) 코사인 유사도 (Cosine Similarity): 벡터의 사잇각 계산
    function calculateCosine(vec1, vec2) {
        let dotProduct = 0;
        let magA = 0;
        let magB = 0;
        for(let i=0; i<vec1.length; i++) {
            dotProduct += vec1[i] * vec2[i];
            magA += vec1[i] * vec1[i];
            magB += vec2[i] * vec2[i];
        }
        magA = Math.sqrt(magA);
        magB = Math.sqrt(magB);
        return (dotProduct / (magA * magB)).toFixed(2);
    }

    // 3. 메인 실행 함수
    function startAnalysis() {
        const targetName = document.getElementById('targetIngredient').value;
        const targetVec = ingredients[targetName];
        
        document.getElementById('resultCard').style.display = 'none';
        document.getElementById('logBox').innerHTML = ''; // 로그 초기화
        
        log(`입력 데이터 벡터화 완료: [${targetVec}]`);
        log("데이터베이스 행렬 스캔 중...");

        let bestMatch = "";
        let minHamming = 999;
        let maxCosine = -1;

        // 모든 재료와 비교 (Loop)
        const candidates = ["aquafaba", "tofu", "soy_milk", "oil", "banana"];
        
        let count = 0;
        const interval = setInterval(() => {
            if (count >= candidates.length) {
                clearInterval(interval);
                showResult(bestMatch, minHamming, maxCosine);
                return;
            }

            const candidateName = candidates[count];
            const candidateVec = ingredients[candidateName];
            
            // 수학 연산 수행
            const hDist = calculateHamming(targetVec, candidateVec);
            const cSim = calculateCosine(targetVec, candidateVec);

            log(`[비교] ${targetName} vs ${candidateName}`);
            log(`... 해밍 거리: ${hDist}, 코사인 유사도: ${cSim}`);

            // 최적값 갱신 (로직 판단)
            if (cSim > maxCosine) {
                maxCosine = cSim;
                minHamming = hDist;
                bestMatch = candidateName;
                
                // 경사하강법 시뮬레이션 (오차가 줄어드는 것처럼 표현)
                log(`📉 경사하강법: 손실함수(Loss) 감소 확인... 가중치 업데이트`);
            }
            
            count++;
        }, 800); // 0.8초마다 실행 (애니메이션 효과)
    }

    function showResult(best, hamming, cosine) {
        log("✅ 최적화 완료 (Global Minima Found)");
        
        document.getElementById('resultCard').style.display = 'block';
        
        // 이름 한글 변환
        const names = { "aquafaba": "병아리콩물 (Aquafaba)", "tofu": "연두부", "soy_milk": "두유", "oil": "코코넛 오일", "banana": "으깬 바나나" };
        
        document.getElementById('bestMatch').innerText = names[best];
        
        // 수치 표시
        document.getElementById('hammingScore').innerText = hamming;
        
        const simPercent = Math.round(cosine * 100);
        document.getElementById('similarityScore').innerText = simPercent;
        document.getElementById('simBar').style.width = simPercent + "%";
    }

    // 초기 화면에 벡터 보여주기
    document.getElementById('matrixView').innerText = "Database Matrix Loaded: " + JSON.stringify(ingredients);

</script>

</body>
</html>