// RailKit official SDK wrapper for Python
const { configure, getAvailability } = require('railkit');

const args = process.argv.slice(2);
if (args.length < 6) {
    console.error(JSON.stringify({ success: false, error: "Usage: node railkit_wrapper.js <trainNo> <from> <to> <date> <coach> <quota>" }));
    process.exit(1);
}

const [trainNo, fromStnCode, toStnCode, date, coach, quota] = args;
const apiKey = process.env.RAILKIT_API_KEY;

if (!apiKey) {
    console.error(JSON.stringify({ success: false, error: "RAILKIT_API_KEY not set" }));
    process.exit(1);
}

// Configure RailKit SDK
configure(apiKey);

// Call getAvailability
(async () => {
    try {
        const result = await getAvailability(trainNo, fromStnCode, toStnCode, date, coach, quota);
        console.log(JSON.stringify(result));
    } catch (error) {
        // Output detailed error for debugging
        console.error(JSON.stringify({ 
            success: false, 
            error: error.message,
            stack: error.stack,
            name: error.name
        }));
        process.exit(1);
    }
})();
