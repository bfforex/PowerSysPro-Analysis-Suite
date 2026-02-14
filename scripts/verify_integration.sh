#!/bin/bash
# PwrSysPro Analysis Suite - Architecture Integration Verification
# This script checks that all components are properly integrated

set -e

echo "🔍 PwrSysPro Architecture Integration Check"
echo "=" | tr '=' '='  | head -c 70
echo ""
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass_count=0
fail_count=0

check_pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    ((pass_count++))
}

check_fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    ((fail_count++))
}

check_warn() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1"
}

echo "📁 Phase 1: Backend File Structure"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check server files
files=(
    "server/main.py:Main API application"
    "server/models/database.py:Database models"
    "server/seed_database.py:Database seeding"
    "server/requirements.txt:Python dependencies"
)

for item in "${files[@]}"; do
    IFS=':' read -r file desc <<< "$item"
    if [ -f "$file" ]; then
        check_pass "$desc ($file)"
    else
        check_fail "$desc missing ($file)"
    fi
done

echo ""
echo "📁 Phase 2: Backend Utility Modules"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

utils=(
    "server/utils/calculations.py:Phase 1 - Basic calculations"
    "server/utils/tagging.py:Phase 1 - Auto-tagging"
    "server/utils/topology.py:Phase 2 - Graph engine"
    "server/utils/tagging_enhanced.py:Phase 2 - Enhanced tagging"
    "server/utils/serialization.py:Phase 2 - File format"
    "server/utils/per_unit.py:Phase 3 - Per-unit system"
    "server/utils/short_circuit.py:Phase 3 - IEC 60909"
    "server/utils/load_flow.py:Phase 3 - Newton-Raphson"
    "server/utils/integrated_calc.py:Phase 3 - Integrated service"
    "server/utils/arc_flash.py:Phase 4 - IEEE 1584"
    "server/utils/report_generator.py:Phase 4 - PDF reports"
    "server/utils/protection.py:Phase 4 - TCC coordination"
)

for item in "${utils[@]}"; do
    IFS=':' read -r file desc <<< "$item"
    if [ -f "$file" ]; then
        check_pass "$desc ($file)"
    else
        check_fail "$desc missing ($file)"
    fi
done

echo ""
echo "📁 Phase 3: Frontend Components"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

components=(
    "client/src/App.jsx:Main application"
    "client/src/main.jsx:React entry point"
    "client/src/components/Canvas.jsx:Phase 1 - ReactFlow canvas"
    "client/src/components/ComponentLibrary.jsx:Phase 1 - Component browser"
    "client/src/components/PropertyInspector.jsx:Phase 1 - Properties panel"
    "client/src/components/ElectricalNode.jsx:Phase 1 - Custom nodes"
    "client/src/components/TopologyViewer.jsx:Phase 2 - Topology viewer"
    "client/src/components/FileOperations.jsx:Phase 2 - Import/Export"
    "client/src/components/NetworkAnalysis.jsx:Phase 3 - Analysis results"
    "client/src/components/ReportGenerator.jsx:Phase 4 - PDF generation"
)

for item in "${components[@]}"; do
    IFS=':' read -r file desc <<< "$item"
    if [ -f "$file" ]; then
        check_pass "$desc ($file)"
    else
        check_fail "$desc missing ($file)"
    fi
done

echo ""
echo "📁 Phase 4: Frontend Services & Config"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

frontend_files=(
    "client/src/services/api.js:API client service"
    "client/src/index.css:Main stylesheet"
    "client/index.html:HTML entry point"
    "client/package.json:NPM dependencies"
    "client/vite.config.js:Vite configuration"
    "client/tailwind.config.js:Tailwind CSS config"
    "client/postcss.config.js:PostCSS config"
)

for item in "${frontend_files[@]}"; do
    IFS=':' read -r file desc <<< "$item"
    if [ -f "$file" ]; then
        check_pass "$desc ($file)"
    else
        check_fail "$desc missing ($file)"
    fi
done

echo ""
echo "🔧 Phase 5: Build & Startup Scripts"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

scripts=(
    "start.sh:Startup script"
    "stop.sh:Shutdown script"
)

for item in "${scripts[@]}"; do
    IFS=':' read -r file desc <<< "$item"
    if [ -f "$file" ]; then
        if [ -x "$file" ]; then
            check_pass "$desc ($file) - executable"
        else
            check_warn "$desc ($file) - not executable"
        fi
    else
        check_fail "$desc missing ($file)"
    fi
done

echo ""
echo "🔍 Phase 6: Python Import Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check Python syntax
cd server

python_files=(
    "main.py"
    "models/database.py"
    "utils/calculations.py"
    "utils/topology.py"
    "utils/per_unit.py"
    "utils/short_circuit.py"
    "utils/load_flow.py"
    "utils/integrated_calc.py"
    "utils/arc_flash.py"
    "utils/report_generator.py"
    "utils/protection.py"
)

for file in "${python_files[@]}"; do
    if python3 -m py_compile "$file" 2>/dev/null; then
        check_pass "Syntax valid: $file"
    else
        check_fail "Syntax error in: $file"
    fi
done

cd ..

echo ""
echo "🔍 Phase 7: Cross-Module Integration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check critical import chains
echo "Checking Phase 3 → Phase 4 integration..."
if grep -q "from utils.short_circuit import" server/utils/arc_flash.py 2>/dev/null; then
    check_pass "Arc flash imports short circuit module"
else
    check_warn "Arc flash may not import short circuit (optional)"
fi

if grep -q "from utils.integrated_calc import" server/main.py 2>/dev/null; then
    check_pass "Main API imports integrated calculator"
else
    check_fail "Main API missing integrated calculator import"
fi

echo ""
echo "Checking Phase 2 → Phase 3 integration..."
if grep -q "from utils.topology import" server/utils/integrated_calc.py 2>/dev/null; then
    check_pass "Integrated calc imports topology"
else
    check_fail "Integrated calc missing topology import"
fi

echo ""
echo "📊 Integration Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}Passed: $pass_count${NC}"
echo -e "${RED}Failed: $fail_count${NC}"
echo ""

if [ $fail_count -eq 0 ]; then
    echo -e "${GREEN}🎉 All integration checks passed!${NC}"
    echo "Architecture is complete and properly integrated."
    exit 0
else
    echo -e "${RED}⚠️  Some integration checks failed.${NC}"
    echo "Please review the failures above."
    exit 1
fi
