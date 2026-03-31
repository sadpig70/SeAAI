#!/usr/bin/env python3
"""
Signalion Browser Engine — Platform-Specific Extractors
각 플랫폼의 JS 추출 코드를 정의. browser_evaluate로 실행.

사용법: Signalion이 MCP browser_evaluate에 이 JS 코드를 전달.
"""

# === GitHub Trending ===
GITHUB_TRENDING_JS = """() => {
    const repos = [];
    document.querySelectorAll('article.Box-row').forEach(el => {
        const nameEl = el.querySelector('h2 a');
        const descEl = el.querySelector('p');
        const langEl = el.querySelector('[itemprop="programmingLanguage"]');
        const starsEl = el.querySelector('a[href$="/stargazers"]');
        const todayEl = el.querySelector('.float-sm-right, span.d-inline-block.float-sm-right');

        const fullName = nameEl ? nameEl.textContent.trim().replace(/\\s+/g, '') : '';
        const [owner, name] = fullName.split('/').map(s => s.trim());

        repos.push({
            owner: owner || '',
            name: name || '',
            description: descEl ? descEl.textContent.trim() : '',
            language: langEl ? langEl.textContent.trim() : '',
            stars: starsEl ? parseInt(starsEl.textContent.trim().replace(/,/g, '')) : 0,
            stars_today: todayEl ? parseInt(todayEl.textContent.trim().replace(/,/g, '')) : 0,
        });
    });
    return JSON.stringify(repos);
}"""

# === Hacker News ===
HN_FRONTPAGE_JS = """() => {
    const stories = [];
    document.querySelectorAll('.titleline > a').forEach((a, i) => {
        stories.push({
            rank: i + 1,
            title: a.textContent.trim(),
            url: a.href,
        });
    });
    // 포인트와 코멘트 수 추출
    document.querySelectorAll('.subtext').forEach((sub, i) => {
        if (i < stories.length) {
            const scoreEl = sub.querySelector('.score');
            const commentsEl = Array.from(sub.querySelectorAll('a')).pop();
            stories[i].points = scoreEl ? parseInt(scoreEl.textContent) : 0;
            stories[i].comments = commentsEl && commentsEl.textContent.includes('comment')
                ? parseInt(commentsEl.textContent) : 0;
        }
    });
    return JSON.stringify(stories.slice(0, 30));
}"""

# === arXiv Search Results ===
ARXIV_SEARCH_JS = """() => {
    const papers = [];
    document.querySelectorAll('.arxiv-result').forEach(el => {
        const titleEl = el.querySelector('.title');
        const authorsEl = el.querySelector('.authors');
        const abstractEl = el.querySelector('.abstract-full') || el.querySelector('.abstract-short');
        const linkEl = el.querySelector('.list-title a');

        papers.push({
            title: titleEl ? titleEl.textContent.replace('Title:', '').trim() : '',
            authors: authorsEl ? authorsEl.textContent.replace('Authors:', '').trim() : '',
            abstract: abstractEl ? abstractEl.textContent.replace('△ Less', '').replace('▽ More', '').trim().slice(0, 500) : '',
            url: linkEl ? linkEl.href : '',
        });
    });
    return JSON.stringify(papers);
}"""

# === HuggingFace Trending Models ===
HF_TRENDING_JS = """() => {
    const models = [];
    document.querySelectorAll('article').forEach(el => {
        const nameEl = el.querySelector('h4') || el.querySelector('a');
        const likesEl = el.querySelector('[class*="likes"]') || el.querySelector('button');

        models.push({
            name: nameEl ? nameEl.textContent.trim() : '',
            url: el.querySelector('a') ? el.querySelector('a').href : '',
        });
    });
    return JSON.stringify(models.slice(0, 20));
}"""

# === Product Hunt Daily ===
PH_DAILY_JS = """() => {
    const products = [];
    document.querySelectorAll('a[href*="/products/"]').forEach(a => {
        const text = a.textContent.trim();
        const match = text.match(/^(\\d+)\\.\\s+(.+)/);
        if (!match) return;
        const rank = parseInt(match[1]);
        const name = match[2];
        const parent = a.parentElement;
        const sibling = parent ? parent.nextElementSibling : null;
        const desc = sibling ? sibling.textContent.trim() : '';
        const grandparent = a.closest('div') ? a.closest('div').parentElement : null;
        const buttons = grandparent ? grandparent.querySelectorAll('button') : [];
        let votes = 0;
        buttons.forEach(b => {
            const v = parseInt(b.textContent.replace(/,/g, ''));
            if (v > votes) votes = v;
        });
        if (!products.find(p => p.name === name)) {
            products.push({ rank, name, url: a.href, description: desc.slice(0, 100), votes });
        }
    });
    return JSON.stringify(products.slice(0, 15));
}"""

# === Devpost Project Gallery ===
DEVPOST_GALLERY_JS = """() => {
    const projects = [];
    document.querySelectorAll('.gallery-item, .software-entry').forEach(el => {
        const nameEl = el.querySelector('h5, .software-entry-name, h4');
        const descEl = el.querySelector('p, .software-entry-description');
        const linkEl = el.querySelector('a[href*="devpost.com/software"]');

        projects.push({
            name: nameEl ? nameEl.textContent.trim() : '',
            description: descEl ? descEl.textContent.trim().slice(0, 200) : '',
            url: linkEl ? linkEl.href : '',
        });
    });
    return JSON.stringify(projects.slice(0, 20));
}"""

# === GeekNews (한국) ===
GEEKNEWS_JS = """() => {
    const items = [];
    document.querySelectorAll('.topic_row').forEach(row => {
        const rankEl = row.querySelector('.votenum');
        const titleA = row.querySelector('.topictitle > a');
        const descA = row.querySelector('.topicdesc > a');
        const metaDiv = row.querySelector('.topicinfo');
        const metaText = metaDiv ? metaDiv.textContent : '';
        const pointsMatch = metaText.match(/(\\d+)\\s*points?/);
        const commentsMatch = metaText.match(/댓글\\s*(\\d+)/);
        if (titleA) {
            items.push({
                rank: rankEl ? parseInt(rankEl.textContent) : 0,
                title: titleA.textContent.trim(),
                url: titleA.href,
                description: descA ? descA.textContent.trim().slice(0, 100) : '',
                points: pointsMatch ? parseInt(pointsMatch[1]) : 0,
                comments: commentsMatch ? parseInt(commentsMatch[1]) : 0,
            });
        }
    });
    return JSON.stringify(items.slice(0, 20));
}"""

# === 추출기 레지스트리 ===
EXTRACTORS = {
    "github_trending": {
        "url": "https://github.com/trending",
        "js": GITHUB_TRENDING_JS,
        "description": "GitHub 일간 트렌딩 repos",
    },
    "hn_frontpage": {
        "url": "https://news.ycombinator.com",
        "js": HN_FRONTPAGE_JS,
        "description": "Hacker News 프론트페이지 기사",
    },
    "arxiv_search": {
        "url_template": "https://arxiv.org/search/?query={query}&searchtype=all&order=-announced_date_first",
        "js": ARXIV_SEARCH_JS,
        "description": "arXiv 검색 결과",
    },
    "hf_trending": {
        "url": "https://huggingface.co/models?sort=trending",
        "js": HF_TRENDING_JS,
        "description": "HuggingFace 트렌딩 모델",
    },
    "producthunt_daily": {
        "url": "https://www.producthunt.com",
        "js": PH_DAILY_JS,
        "description": "Product Hunt 일간 신제품",
    },
    "geeknews": {
        "url": "https://news.hada.io",
        "js": GEEKNEWS_JS,
        "description": "GeekNews 한국 기술 뉴스 (HN 한국판)",
    },
    "devpost_gallery": {
        "url_template": "https://{hackathon}.devpost.com/project-gallery",
        "js": DEVPOST_GALLERY_JS,
        "description": "Devpost 해커톤 프로젝트 갤러리",
    },
}
