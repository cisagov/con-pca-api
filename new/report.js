const puppeteer = require("puppeteer");

async function getReport(cycleUuid, reportType, nonhuman) {
  const browser = await puppeteer.launch({
    headless: true,
    executablePath: "/usr/bin/chromium",
    args: ["--no-sandbox"],
  });
  const page = await browser.newPage();
  let url = `http://localhost:5000/api/cycle/${cycleUuid}/reports/${reportType}/`;
  if (nonhuman === "True") {
    url += "?nonhuman=true";
  }
  await page.goto(url, { waitUntil: "networkidle2" });
  await page.emulateMediaType("screen");
  const filename = `${cycleUuid}_${reportType}.pdf`;
  pdfContent = await page.pdf({
    format: "letter",
    path: filename,
    pageRanges: "1",
  });
  console.log(filename);
  await page.close();
  await browser.close();
}
const args = process.argv.slice(2);
getReport(args[0], args[1], args[2]);
