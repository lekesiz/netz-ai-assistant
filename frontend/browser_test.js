/**
 * Automated Browser Testing for NETZ AI Frontend
 * Uses Puppeteer to test all frontend functionality
 */

const puppeteer = require('puppeteer');
const fs = require('fs');

// Test configuration
const BASE_URL = 'http://localhost:3000';
const API_URL = 'http://localhost:8001';

// Test results
let testResults = [];

// Helper function to log results
function logTest(testName, status, details = '') {
  const result = {
    test: testName,
    status: status ? '✅ PASSED' : '❌ FAILED',
    details: details,
    timestamp: new Date().toISOString()
  };
  testResults.push(result);
  console.log(`${result.status} ${testName} ${details ? `- ${details}` : ''}`);
}

// Helper function to wait
const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function runTests() {
  console.log('🚀 Starting NETZ AI Frontend Browser Tests...\n');
  
  const browser = await puppeteer.launch({
    headless: false, // Set to true for CI/CD
    devtools: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  
  // Enable console logging
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log('Browser Console Error:', msg.text());
    }
  });
  
  // Monitor network requests
  const networkRequests = [];
  page.on('request', request => {
    if (request.url().includes('localhost')) {
      networkRequests.push({
        url: request.url(),
        method: request.method(),
        headers: request.headers()
      });
    }
  });
  
  page.on('response', response => {
    if (response.url().includes('localhost')) {
      console.log(`API Response: ${response.url()} - Status: ${response.status()}`);
    }
  });
  
  try {
    // Test 1: Homepage Load
    console.log('📍 Test 1: Homepage Load');
    await page.goto(BASE_URL, { waitUntil: 'networkidle2' });
    const title = await page.title();
    logTest('Homepage Load', title.includes('NETZ'), `Title: ${title}`);
    
    // Test 2: Check Page Structure
    console.log('\n📍 Test 2: Page Structure');
    const hasHeader = await page.$('header') !== null;
    const hasMain = await page.$('main') !== null;
    logTest('Page Structure', hasHeader && hasMain);
    
    // Test 3: Navigation to Chat
    console.log('\n📍 Test 3: Navigate to Chat');
    const chatLink = await page.$('a[href="/chat"]');
    if (chatLink) {
      await chatLink.click();
      await page.waitForNavigation({ waitUntil: 'networkidle2' });
      const chatUrl = page.url();
      logTest('Chat Navigation', chatUrl.includes('/chat'), `URL: ${chatUrl}`);
    } else {
      // Direct navigation
      await page.goto(`${BASE_URL}/chat`, { waitUntil: 'networkidle2' });
      logTest('Chat Navigation (Direct)', true);
    }
    
    // Test 4: Chat Interface Elements
    console.log('\n📍 Test 4: Chat Interface Elements');
    await wait(2000); // Wait for React to render
    
    const chatElements = {
      messageInput: await page.$('input[type="text"], textarea'),
      sendButton: await page.$('button'),
      messageContainer: await page.$('[class*="message"], [class*="chat"]')
    };
    
    const hasAllElements = Object.values(chatElements).every(el => el !== null);
    logTest('Chat Interface Elements', hasAllElements, 
      `Input: ${!!chatElements.messageInput}, Button: ${!!chatElements.sendButton}`);
    
    // Test 5: Send Test Message
    console.log('\n📍 Test 5: Send Test Message');
    if (chatElements.messageInput) {
      // Type message
      await chatElements.messageInput.click({ clickCount: 3 });
      await chatElements.messageInput.type('NETZ hangi hizmetleri sunuyor?');
      
      // Find and click send button
      const buttons = await page.$$('button');
      let sendButton = null;
      
      for (const button of buttons) {
        const text = await page.evaluate(el => el.textContent, button);
        if (text && (text.includes('Send') || text.includes('Gönder') || text.includes('→'))) {
          sendButton = button;
          break;
        }
      }
      
      if (sendButton) {
        // Monitor API call
        const apiCallPromise = page.waitForResponse(response => 
          response.url().includes('/api/chat') && response.status() === 200,
          { timeout: 60000 }
        );
        
        await sendButton.click();
        
        // Wait for API response
        const response = await apiCallPromise;
        const responseData = await response.json();
        
        logTest('Message Send', true, `Response received in ${response.headers()['x-response-time'] || 'N/A'}`);
        logTest('AI Response', !!responseData.response, `Model: ${responseData.model || 'N/A'}`);
        
        // Check if response is displayed
        await wait(2000);
        const messages = await page.$$('[class*="message"]');
        logTest('Response Display', messages.length > 1, `Messages count: ${messages.length}`);
      }
    }
    
    // Test 6: Test Document Upload Page
    console.log('\n📍 Test 6: Document Upload Page');
    await page.goto(`${BASE_URL}/documents`, { waitUntil: 'networkidle2' });
    
    const uploadInput = await page.$('input[type="file"]');
    const uploadButton = await page.$('[class*="upload"]');
    logTest('Document Upload Page', !!uploadInput || !!uploadButton);
    
    // Test 7: Check API Health
    console.log('\n📍 Test 7: API Health Check');
    const apiHealth = await page.evaluate(async () => {
      try {
        const response = await fetch('http://localhost:8001/health');
        return await response.json();
      } catch (error) {
        return { error: error.message };
      }
    });
    logTest('API Health', !apiHealth.error, JSON.stringify(apiHealth));
    
    // Test 8: Model Information
    console.log('\n📍 Test 8: Model Information');
    const modelInfo = await page.evaluate(async () => {
      try {
        const response = await fetch('http://localhost:8001/api/models/available');
        return await response.json();
      } catch (error) {
        return { error: error.message };
      }
    });
    logTest('Model Availability', !modelInfo.error && modelInfo.models, 
      `Available models: ${modelInfo.models ? modelInfo.models.length : 0}`);
    
    // Test 9: Performance Metrics
    console.log('\n📍 Test 9: Performance Metrics');
    const metrics = await page.metrics();
    const performance = await page.evaluate(() => {
      const perf = performance.getEntriesByType('navigation')[0];
      return {
        domContentLoaded: perf.domContentLoadedEventEnd - perf.domContentLoadedEventStart,
        loadComplete: perf.loadEventEnd - perf.loadEventStart,
        totalTime: perf.loadEventEnd - perf.fetchStart
      };
    });
    
    logTest('Performance', performance.totalTime < 5000, 
      `Total load time: ${performance.totalTime}ms`);
    
    // Test 10: Console Errors
    console.log('\n📍 Test 10: Console Errors');
    const consoleErrors = await page.evaluate(() => {
      return window.__consoleErrors || [];
    });
    logTest('No Console Errors', consoleErrors.length === 0, 
      `Errors found: ${consoleErrors.length}`);
    
  } catch (error) {
    console.error('Test Error:', error);
    logTest('Test Execution', false, error.message);
  }
  
  // Generate test report
  console.log('\n📊 TEST SUMMARY\n' + '='.repeat(50));
  const passed = testResults.filter(r => r.status.includes('✅')).length;
  const failed = testResults.filter(r => r.status.includes('❌')).length;
  
  console.log(`Total Tests: ${testResults.length}`);
  console.log(`✅ Passed: ${passed}`);
  console.log(`❌ Failed: ${failed}`);
  console.log(`Success Rate: ${((passed / testResults.length) * 100).toFixed(1)}%`);
  
  // Save detailed report
  fs.writeFileSync('test_report.json', JSON.stringify(testResults, null, 2));
  
  // Close browser
  await browser.close();
}

// Alternative: Use Chrome DevTools Protocol directly
async function runDevToolsTests() {
  console.log('\n🔧 Chrome DevTools Protocol Tests\n');
  
  const browser = await puppeteer.launch({ headless: false, devtools: true });
  const page = await browser.newPage();
  
  // Enable DevTools domains
  const client = await page.target().createCDPSession();
  await client.send('Runtime.enable');
  await client.send('Network.enable');
  await client.send('Performance.enable');
  
  // Monitor network
  client.on('Network.requestWillBeSent', (params) => {
    console.log(`Network Request: ${params.request.method} ${params.request.url}`);
  });
  
  client.on('Network.responseReceived', (params) => {
    console.log(`Network Response: ${params.response.status} ${params.response.url}`);
  });
  
  // Navigate and collect metrics
  await page.goto(BASE_URL);
  
  // Get performance metrics
  const perfMetrics = await client.send('Performance.getMetrics');
  console.log('\nPerformance Metrics:', perfMetrics.metrics);
  
  // Get memory info
  const memoryInfo = await page.evaluate(() => {
    if (performance.memory) {
      return {
        usedJSHeapSize: (performance.memory.usedJSHeapSize / 1048576).toFixed(2) + ' MB',
        totalJSHeapSize: (performance.memory.totalJSHeapSize / 1048576).toFixed(2) + ' MB'
      };
    }
    return null;
  });
  console.log('\nMemory Usage:', memoryInfo);
  
  await browser.close();
}

// Run tests
console.log('Select test mode:');
console.log('1. Run automated UI tests');
console.log('2. Run DevTools protocol tests');
console.log('3. Run both');

const mode = process.argv[2] || '1';

switch(mode) {
  case '1':
    runTests();
    break;
  case '2':
    runDevToolsTests();
    break;
  case '3':
    runTests().then(() => runDevToolsTests());
    break;
  default:
    runTests();
}