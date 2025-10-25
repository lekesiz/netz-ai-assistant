#!/bin/bash
# NETZ AI Integrations API Test Script
# Tests all integration endpoints

echo "🔌 NETZ AI Integrations API - Test Script"
echo "========================================"
echo ""

API_BASE_URL="http://localhost:8000"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Get Integrations Status
echo -e "${YELLOW}Test 1: Getting integrations status...${NC}"
curl -s "${API_BASE_URL}/api/integrations/status" | python3 -m json.tool || echo -e "${RED}❌ Failed${NC}"
echo ""

# Test 2: Trigger Google Drive Sync
echo -e "${YELLOW}Test 2: Triggering Google Drive sync...${NC}"
curl -X POST -s "${API_BASE_URL}/api/integrations/drive/sync" \
  -H "Content-Type: application/json" \
  -d '{"folder_names": ["NETZ Clients", "NETZ Documents"]}' | python3 -m json.tool || echo -e "${RED}❌ Failed${NC}"
echo ""

# Test 3: Trigger Gmail Sync
echo -e "${YELLOW}Test 3: Triggering Gmail sync...${NC}"
curl -X POST -s "${API_BASE_URL}/api/integrations/gmail/sync" \
  -H "Content-Type: application/json" \
  -d '{"days_back": 365, "max_results": 1000}' | python3 -m json.tool || echo -e "${RED}❌ Failed${NC}"
echo ""

# Test 4: Trigger Wedof Sync
echo -e "${YELLOW}Test 4: Triggering Wedof sync...${NC}"
curl -X POST -s "${API_BASE_URL}/api/integrations/wedof/sync" \
  -H "Content-Type: application/json" \
  -d '{"sync_stagiaires": true, "sync_formations": true}' | python3 -m json.tool || echo -e "${RED}❌ Failed${NC}"
echo ""

# Test 5: Trigger All Syncs
echo -e "${YELLOW}Test 5: Triggering all syncs...${NC}"
curl -X POST -s "${API_BASE_URL}/api/integrations/sync-all" | python3 -m json.tool || echo -e "${RED}❌ Failed${NC}"
echo ""

# Test 6: Get Google Drive History
echo -e "${YELLOW}Test 6: Getting Google Drive sync history...${NC}"
curl -s "${API_BASE_URL}/api/integrations/google_drive/history?limit=5" | python3 -m json.tool || echo -e "${RED}❌ Failed${NC}"
echo ""

# Test 7: Get Gmail History
echo -e "${YELLOW}Test 7: Getting Gmail sync history...${NC}"
curl -s "${API_BASE_URL}/api/integrations/gmail/history?limit=5" | python3 -m json.tool || echo -e "${RED}❌ Failed${NC}"
echo ""

# Test 8: Get Wedof History
echo -e "${YELLOW}Test 8: Getting Wedof sync history...${NC}"
curl -s "${API_BASE_URL}/api/integrations/wedof/history?limit=5" | python3 -m json.tool || echo -e "${RED}❌ Failed${NC}"
echo ""

echo -e "${GREEN}✅ All API tests completed!${NC}"
echo ""
echo "Next steps:"
echo "1. Check logs for any errors"
echo "2. Verify sync history in database"
echo "3. Test with actual API credentials"
