from io import BytesIO
import logging

import pyppeteer
import asyncio

from config import settings


def download_pdf(report_type, uuid, cycle, auth_header=None):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    if settings.LOCAL_API_KEY and auth_header:
        auth_header = settings.LOCAL_API_KEY

    response = loop.run_until_complete(
        _download_pdf(report_type, uuid, cycle, auth_header=auth_header)
    )
    buffer = BytesIO()
    buffer.write(response)
    buffer.seek(0)
    return buffer


async def _download_pdf(report_type, uuid, cycle, auth_header=None):
    browser = await pyppeteer.connect(
        browserWSEndpoint=f"ws://{settings.BROWSERLESS_ENDPOINT}",
        ignoreHTTPSErrors=True,
    )
    page = await browser.newPage()

    if auth_header:
        url = f"{settings.REPORTS_ENDPOINT}/reports/{report_type}/{uuid}/{cycle}?reportToken={auth_header}"
    else:
        url = f"{settings.REPORTS_ENDPOINT}/reports/{report_type}/{uuid}/{cycle}"

    await page.goto(
        url, waitUntil="networkidle2",
    )
    await page.emulateMedia("screen")
    pdf_content = await page.pdf({"format": "Letter", "printBackground": True})
    await page.close()
    return pdf_content
