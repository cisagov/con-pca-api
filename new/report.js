const puppeteer = require("puppeteer");

async function getReport(cycleUuid, reportType) {
  const browser = await puppeteer.launch({
    headless: true,
    executablePath: "/usr/bin/chromium",
    args: ["--no-sandbox"],
  });
  const page = await browser.newPage();
  await page.goto(
    `http://localhost:5000/api/cycle/${cycleUuid}/reports/${reportType}/`,
    { waitUntil: "networkidle2" }
  );
  const filename = `${cycleUuid}_${reportType}.pdf`;
  pdfContent = await page.pdf({
    format: "letter",
    printBackground: true,
    path: filename,
  });
  console.log(filename);
  await page.close();
  await browser.close();
}
const args = process.argv.slice(2);
getReport(args[0], args[1]);
// getReport('699dd0de-32bb-4874-80d2-d6968c4a9312', 'monthly')
