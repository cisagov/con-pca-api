from io import BytesIO

import pyppeteer
import asyncio


def download_pdf(report_type, uuid, cycle, auth_header=None):

    print(auth_header)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    auth_header = auth_header.split(" ")[-1]

    print(
        f"http://pca-web:4200/reports/{report_type}/{uuid}/{cycle}?reportToken={auth_header}"
    )

    response = loop.run_until_complete(
        _download_pdf(report_type, uuid, cycle, auth_header=auth_header.split(" ")[-1])
    )
    buffer = BytesIO()
    buffer.write(response)
    buffer.seek(0)
    return buffer


async def _download_pdf(report_type, uuid, cycle, auth_header=None):
    url = "pca-browserless:3000"
    browser = await pyppeteer.connect(browserWSEndpoint=f"ws://{url}")
    page = await browser.newPage()

    if auth_header:
        url = f"http://pca-web:4200/reports/{report_type}/{uuid}/{cycle}?reportToken={auth_header}"
    else:
        url = f"http://pca-web:4200/reports/{report_type}/{uuid}/{cycle}"

    await page.goto(
        url, waitUntil="networkidle2",
    )
    await page.emulateMedia("screen")
    pdf_content = await page.pdf({"format": "Letter", "printBackground": True})
    await page.close()
    return pdf_content
