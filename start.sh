#!/bin/bash

# SDS Project Startup Script
# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

source sds_demo/bin/activate

echo -e "${BLUE}Starting SDS Project...${NC}\n"

# Start md_parser
echo -e "${GREEN}Starting md_parser...${NC}"
cd md_parser
node server.js &
MD_PARSER_PID=$!
cd ..
sleep 2

# Start api_gateway
echo -e "${GREEN}Starting api_gateway...${NC}"
cd api_gateway
python3 main.py &
API_GATEWAY_PID=$!
cd ..
sleep 2

# Start html_templater
echo -e "${GREEN}Starting html_templater...${NC}"
cd html_templater
python3 main.py &
HTML_TEMPLATER_PID=$!
cd ..
sleep 2

# Start pdf_renderer
echo -e "${GREEN}Starting pdf_renderer...${NC}"
cd pdf_renderer
python3 main.py &
PDF_RENDERER_PID=$!
cd ..
sleep 2

echo -e "${BLUE}All services started!${NC}\n"
echo "PIDs: md_parser=$MD_PARSER_PID, api_gateway=$API_GATEWAY_PID, html_templater=$HTML_TEMPLATER_PID, pdf_renderer=$PDF_RENDERER_PID"

# Open the HTML page in default browser
echo -e "${GREEN}Opening frontend...${NC}"
# For macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    open index.html
# For Linux
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open index.html 2>/dev/null &
# For Windows (Git Bash, WSL, etc.)
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    start index.html
fi

echo -e "${BLUE}Press Ctrl+C to stop all services${NC}\n"

# Cleanup function
cleanup() {
    echo -e "\n${BLUE}Stopping all services...${NC}"
    kill $MD_PARSER_PID $API_GATEWAY_PID $HTML_TEMPLATER_PID $PDF_RENDERER_PID 2>/dev/null
    exit 0
}

# Trap Ctrl+C
trap cleanup SIGINT

# Keep script running
wait