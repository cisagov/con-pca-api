"""Report Utils."""
# Standard Python Libraries
import asyncio
from io import BytesIO

# Third-Party Libraries
from django.core.handlers.wsgi import WSGIRequest
import pyppeteer
from rest_framework.request import Request

# cisagov Libraries
from config import settings


def is_nonhuman_request(request):
    """Check if a request wants non-human interactions included in reports/stats."""
    if type(request) == Request:
        if str(request.query_params.get("nonhuman")) == "true":
            return True
    elif type(request) == WSGIRequest:
        if str(request.GET.get("nonhuman")) == "true":
            return True
    return False


def download_pdf(report_type, uuid, cycle_uuid, nonhuman=False):
    """Download PDF Report."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    auth_header = settings.LOCAL_API_KEY if settings.LOCAL_API_KEY else None

    response = loop.run_until_complete(
        _download_pdf(
            report_type, uuid, cycle_uuid, auth_header=auth_header, nonhuman=nonhuman
        )
    )

    if response == "500":
        raise Exception("Report Error - Check Logs")

    buffer = BytesIO()
    buffer.write(response)
    buffer.seek(0)
    return buffer


async def _download_pdf(
    report_type, uuid, cycle_uuid, auth_header=None, nonhuman=False
):
    browser = await pyppeteer.connect(
        browserWSEndpoint=f"ws://{settings.BROWSERLESS_ENDPOINT}",
        ignoreHTTPSErrors=True,
    )
    page = await browser.newPage()

    nonhuman = "true" if nonhuman else "false"
    url = f"{settings.REPORTS_ENDPOINT}/reports/{report_type}/{uuid}/{cycle_uuid}/true/{nonhuman}"
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
