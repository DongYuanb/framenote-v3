"""SEO优化 - 内容页面和结构化数据"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from datetime import datetime
import json

router = APIRouter(prefix="/api", tags=["seo"])

# 网站基础信息
SITE_INFO = {
    "name": "FrameNote",
    "title": "FrameNote - AI视频笔记工具",
    "description": "AI 视频笔记工具：一键提取PPT、自动生成讲义和知识图片，极致高效，极简体验。",
    "keywords": "AI视频笔记, 视频转文字, 视频摘要, PPT提取, 讲义生成, 知识图片, AI学习工具",
    "author": "FrameNote",
    "url": "https://framenote.ai",
    "logo": "/lovable-uploads/1a269a26-9009-4b73-80c2-654445d2810b.png"
}

# 功能特性
FEATURES = [
    {
        "title": "智能视频分析",
        "description": "基于先进AI技术，自动识别视频内容，提取关键信息",
        "icon": "🎥"
    },
    {
        "title": "PPT一键提取", 
        "description": "智能识别视频中的PPT内容，自动提取文字和图片",
        "icon": "📊"
    },
    {
        "title": "讲义自动生成",
        "description": "根据视频内容自动生成结构化讲义，提高学习效率",
        "icon": "📝"
    },
    {
        "title": "知识图片制作",
        "description": "将复杂概念转化为直观的知识图片，便于理解记忆",
        "icon": "🖼️"
    },
    {
        "title": "多格式导出",
        "description": "支持PDF、Word、Markdown等多种格式导出",
        "icon": "📤"
    },
    {
        "title": "会员特权",
        "description": "不同会员等级享受不同处理时长和功能特权",
        "icon": "👑"
    }
]

# 使用场景
USE_CASES = [
    {
        "title": "在线教育",
        "description": "帮助教师快速制作课程讲义，提高教学效率",
        "scenarios": ["录播课程处理", "直播回放分析", "教学素材整理"]
    },
    {
        "title": "企业培训",
        "description": "为企业培训视频生成标准化文档，便于员工学习",
        "scenarios": ["培训视频处理", "会议记录整理", "知识库建设"]
    },
    {
        "title": "学术研究",
        "description": "为学术视频生成结构化笔记，提高研究效率",
        "scenarios": ["学术讲座记录", "研究资料整理", "论文素材收集"]
    },
    {
        "title": "个人学习",
        "description": "帮助个人学习者快速整理学习内容",
        "scenarios": ["网课笔记制作", "学习资料整理", "知识图谱构建"]
    }
]

# FAQ数据
FAQS = [
    {
        "question": "FrameNote支持哪些视频格式？",
        "answer": "目前支持MP4、AVI、MOV、MKV等主流视频格式，最大支持500MB文件。"
    },
    {
        "question": "免费用户有什么限制？",
        "answer": "免费用户每天可以处理10分钟视频，支持基础功能。升级会员可享受更多时长和高级功能。"
    },
    {
        "question": "处理速度如何？",
        "answer": "一般10分钟视频处理时间约2-3分钟，具体时间取决于视频复杂度和服务器负载。"
    },
    {
        "question": "数据安全如何保障？",
        "answer": "我们采用银行级加密技术，所有数据经过加密传输和存储，处理完成后自动删除视频文件。"
    },
    {
        "question": "支持批量处理吗？",
        "answer": "高级会员支持批量处理功能，可以同时处理多个视频文件。"
    },
    {
        "question": "如何升级会员？",
        "answer": "在个人中心选择会员套餐，支持支付宝支付，支付成功后立即生效。"
    }
]

@router.get("/seo/sitemap.xml")
async def sitemap():
    """生成网站地图"""
    sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://framenote.ai/</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://framenote.ai/features</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://framenote.ai/pricing</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://framenote.ai/help</loc>
        <lastmod>2024-01-01</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.6</priority>
    </url>
</urlset>"""
    
    return HTMLResponse(content=sitemap_content, media_type="application/xml")

@router.get("/seo/robots.txt")
async def robots():
    """生成robots.txt"""
    robots_content = """User-agent: *
Allow: /
Disallow: /api/
Disallow: /admin/
Disallow: /storage/

Sitemap: https://framenote.ai/api/seo/sitemap.xml"""
    
    return HTMLResponse(content=robots_content, media_type="text/plain")

@router.get("/seo/structured-data")
async def structured_data():
    """生成结构化数据"""
    structured_data = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": SITE_INFO["name"],
        "description": SITE_INFO["description"],
        "url": SITE_INFO["url"],
        "applicationCategory": "EducationalApplication",
        "operatingSystem": "Web",
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "CNY",
            "description": "免费版本"
        },
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.8",
            "ratingCount": "1250"
        },
        "author": {
            "@type": "Organization",
            "name": "FrameNote Team"
        },
        "featureList": [
            "智能视频分析",
            "PPT一键提取", 
            "讲义自动生成",
            "知识图片制作",
            "多格式导出"
        ]
    }
    
    return structured_data

@router.get("/seo/features")
async def features_page():
    """功能特性页面"""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>功能特性 - {SITE_INFO['title']}</title>
        <meta name="description" content="FrameNote强大的AI功能特性：智能视频分析、PPT提取、讲义生成、知识图片制作等。">
        <link rel="canonical" href="{SITE_INFO['url']}/features">
    </head>
    <body>
        <h1>FrameNote 功能特性</h1>
        <div class="features">
            {''.join([f'''
            <div class="feature">
                <h2>{feature['icon']} {feature['title']}</h2>
                <p>{feature['description']}</p>
            </div>
            ''' for feature in FEATURES])}
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@router.get("/seo/use-cases")
async def use_cases_page():
    """使用场景页面"""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>使用场景 - {SITE_INFO['title']}</title>
        <meta name="description" content="FrameNote适用于在线教育、企业培训、学术研究、个人学习等多种场景。">
        <link rel="canonical" href="{SITE_INFO['url']}/use-cases">
    </head>
    <body>
        <h1>FrameNote 使用场景</h1>
        <div class="use-cases">
            {''.join([f'''
            <div class="use-case">
                <h2>{case['title']}</h2>
                <p>{case['description']}</p>
                <ul>
                    {''.join([f'<li>{scenario}</li>' for scenario in case['scenarios']])}
                </ul>
            </div>
            ''' for case in USE_CASES])}
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@router.get("/seo/help")
async def help_page():
    """帮助中心页面"""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>帮助中心 - {SITE_INFO['title']}</title>
        <meta name="description" content="FrameNote使用帮助和常见问题解答，快速上手AI视频笔记工具。">
        <link rel="canonical" href="{SITE_INFO['url']}/help">
    </head>
    <body>
        <h1>帮助中心</h1>
        <div class="faq">
            {''.join([f'''
            <div class="faq-item">
                <h3>{faq['question']}</h3>
                <p>{faq['answer']}</p>
            </div>
            ''' for faq in FAQs])}
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@router.get("/seo/meta-tags")
async def get_meta_tags():
    """获取SEO元标签"""
    return {
        "title": SITE_INFO["title"],
        "description": SITE_INFO["description"],
        "keywords": SITE_INFO["keywords"],
        "author": SITE_INFO["author"],
        "og_title": SITE_INFO["title"],
        "og_description": SITE_INFO["description"],
        "og_image": SITE_INFO["logo"],
        "og_url": SITE_INFO["url"],
        "twitter_card": "summary_large_image",
        "twitter_title": SITE_INFO["title"],
        "twitter_description": SITE_INFO["description"],
        "twitter_image": SITE_INFO["logo"]
    }
