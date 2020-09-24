from io import BytesIO

import pyppeteer
import asyncio
from contextlib import suppress

from config import settings


def download_pdf(report_type, uuid, cycle, cycle_uuid=None):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    auth_header = settings.LOCAL_API_KEY if settings.LOCAL_API_KEY else None

    response = loop.run_until_complete(
        _download_pdf(
            report_type, uuid, cycle, auth_header=auth_header, cycle_uuid=cycle_uuid
        )
    )

    with suppress(asyncio.exceptions.CancelledError):
        pending = asyncio.Task.all_tasks()
        loop.run_until_complete(asyncio.gather(*pending))

    if response == "500":
        raise Exception("Report Error - Check Logs")

    buffer = BytesIO()
    buffer.write(response)
    buffer.seek(0)
    return buffer


async def _download_pdf(report_type, uuid, cycle, auth_header=None, cycle_uuid=None):
    browser = await pyppeteer.connect(
        browserWSEndpoint=f"ws://{settings.BROWSERLESS_ENDPOINT}",
        ignoreHTTPSErrors=True,
    )
    page = await browser.newPage()

    url = f"{settings.REPORTS_ENDPOINT}/reports/{report_type}/{uuid}/{cycle}/true"
    if cycle_uuid:
        url += f"/{cycle_uuid}"
    if auth_header:
        url += f"?reportToken={auth_header}"

    responses = []
    page.on("response", lambda response: responses.append(response.status))

    await page.goto(url, waitUntil="networkidle0")
    await page.emulateMedia("screen")
    await page.waitForSelector("#bluePhishLogo")
    await page.waitFor(1500)

    pdf_content = await page.pdf({"format": "Letter", "printBackground": True})
    await page.close()
    await browser.close()

    if 500 in responses:
        return "500"

    return pdf_content
