const axios = require("axios");
const { parseStringPromise } = require("xml2js");
const { exec } = require("node:child_process");
const pLimit = require("p-limit").default;

const SEARCH_URL =
  "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term=cobb+syndrome&field=title&usehistory=y";
const S3_BUCKET = "pmc-oa-opendata/oa_noncomm/txt/all"; // Replace with actual bucket name
const S3_PREFIX = "PMC"; // Adjust prefix if necessary

// Limit concurrent AWS CLI processes to 2
const limit = pLimit(2);

// Function to fetch XML from the URL
async function fetchArticleIDs() {
  try {
    const response = await axios.get(SEARCH_URL);
    const data = await parseStringPromise(response.data);
    const ids = data.eSearchResult.IdList[0].Id.map((id) => id);
    console.log(data.eSearchResult.IdList);
    console.log(`Fetched ${ids.length} IDs: ${ids}`);
    return ids;
  } catch (error) {
    console.error("Error fetching IDs:", error.message);
    return [];
  }
}

// Function to download a file from S3 using AWS CLI
function downloadFromS3(pmcId) {
  return new Promise((resolve, reject) => {
    const s3Key = `${S3_PREFIX}${pmcId}.txt`;
    const command = `aws s3 cp s3://${S3_BUCKET}/${s3Key} --no-sign-request .`;

    console.log(`Starting download: ${s3Key}`);
    exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error(`Failed to download ${s3Key}:`, stderr);
        resolve(error);
      } else {
        console.log(`Downloaded ${s3Key} successfully.`);
        resolve(stdout);
      }
    });
  });
}

// Main function
async function main() {
  const ids = await fetchArticleIDs();
  if (ids.length === 0) return;

  // Process downloads with concurrency limit
  const downloadPromises = ids.map((id) => limit(() => downloadFromS3(id)));
  await Promise.all(downloadPromises);

  console.log("All downloads completed.");
}

main();
