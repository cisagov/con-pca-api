import { launch } from "puppeteer";

async function getReport(filename, cycleId, reportType, nonhuman) {
  const browser = await launch({
    headless: true,
    executablePath: "/usr/bin/chromium",
    args: ["--no-sandbox"],
  });
  const page = await browser.newPage();
  let url = `http://localhost:5000/api/cycle/${cycleId}/reports/${reportType}/`;
  if (nonhuman === "True") {
    url += "?nonhuman=true";
  }

  var failure = false;
  page.on("response", async (response) => {
    if (response.status() == 500) {
      console.log("ERROR generating PDF.");
      failure = true;
    }
  });

  await page.goto(url, { waitUntil: "networkidle2" });

  await page.emulateMediaType("screen");

  if (failure) {
    await page.close();
    await browser.close();
    return;
  }
  if (reportType == "status") {
    pdfContent = await page.pdf({
      format: "letter",
      path: filename,
      pageRanges: "1",
      printBackground: true,
    });
  } else {
    pdfContent = await page.pdf({
      format: "letter",
      path: filename,
      printBackground: true,
    });
  }

  await page.close();
  await browser.close();
}

const args = process.argv.slice(2);
getReport(args[0], args[1], args[2], args[3]);
