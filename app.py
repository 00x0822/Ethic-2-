def generate_content(prompt: str):
    api_key = st.secrets.get("GOOGLE_API_KEY")
    if not api_key:
        st.error("❗ ‘GOOGLE_API_KEY’가 설정되지 않았습니다. Settings → Secrets 에 추가하세요.")
        return ""

    # v1 네임스페이스로 변경
    url = (
        "https://generativelanguage.googleapis.com"
        f"/v1/models/text-bison-001:generateText?key={api_key}"
    )
    headers = {"Content-Type": "application/json; charset=UTF-8"}
    body = {
        "prompt": {"text": prompt},
        "temperature": 0.7,
        "candidateCount": 1,
    }

    try:
        res = requests.post(url, headers=headers, json=body, timeout=30)
        res.raise_for_status()
    except requests.exceptions.HTTPError:
        st.error(f"❗ API 호출 오류 {res.status_code}\n{res.text}")
        return ""
    except requests.exceptions.RequestException as e:
        st.error(f"❗ 네트워크 오류: {e}")
        return ""

    data = res.json()
    return data["candidates"][0]["output"]
