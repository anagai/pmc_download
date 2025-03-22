const axios = require("axios");
const { parseStringPromise } = require("xml2js");
const { exec } = require("node:child_process");
const util = require("node:util");

const execPromise = util.promisify(exec);

const SEARCH_URL =
  "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term=cobb+syndrome&field=title&usehistory=y";
const S3_BUCKET = "pmc-oa-opendata/oa_noncomm/txt/all"; // Replace with actual bucket name
const S3_PREFIX = "PMC"; // Adjust prefix if necessary
const MAX_CONCURRENT_DOWNLOADS = 2; // Limit of concurrent downloads

// Function to fetch article IDs
async function fetchArticleIDs() {
  try {
    const response = await axios.get(SEARCH_URL);
    const data = await parseStringPromise(response.data);
    const ids = data.eSearchResult.IdList[0].Id.map((id) => id);
    console.log(`Fetched ${ids.length} IDs:${data.eSearchResult.IdList[0].Id}`);
    return ids;
  } catch (error) {
    console.error("Error fetching IDs:", error.message);
    return [];
  }
}

// Function to download a file from S3 using AWS CLI
async function downloadFromS3(pmcId) {
  const s3Key = `${S3_PREFIX}${pmcId}.txt`;
  const command = `aws s3 cp s3://${S3_BUCKET}/${s3Key} --no-sign-request .`;

  console.log(`Starting download: ${s3Key}.txt`);
  try {
    let res = await execPromise(command);
    console.log(`Downloaded ${s3Key}.txt successfully.`);
    return res;
  } catch (error) {
    console.error(`Failed to download ${s3Key}.txt:`, error.stderr);
  }
}

// Function to process downloads with concurrency control using Promise.all()
async function processDownloads(ids, concurrencyLimit) {
  for (let i = 0; i < ids.length; i += concurrencyLimit) {
    const batch = ids.slice(i, i + concurrencyLimit);
    console.log(`Processing batch: ${batch.join(", ")}`);

    let resp = await Promise.all(batch.map((id) => downloadFromS3(id))); // Run the batch concurrently
    console.log('resp:', resp);
  }
}

async function main() {
  const ids = await fetchArticleIDs();
  if (ids.length === 0) return;

  await processDownloads(ids, MAX_CONCURRENT_DOWNLOADS);
  console.log("All downloads completed.");
}

main();
