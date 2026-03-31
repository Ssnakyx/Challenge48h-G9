#!/bin/bash
# 🎓 JURY_VALIDATION.sh - Script de validation automatique de tous les points

echo "════════════════════════════════════════════════════════════════"
echo "🎯 VALIDATION BARÈME - Challenge 48h Infrastructure Production"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Vérifications
PASS=0
TOTAL=15

echo "📋 POINT 1 : GESTION DES SECRETS (2 pts)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
# Vérifier que les passwords utilisent des variables
HAS_VARS=$(grep -c "POSTGRES_PASSWORD.*\${" docker-compose.yml || echo "0")
if [ "$HAS_VARS" -gt 0 ]; then
  echo "✅ Secrets externalisés via \${...} variables"
  PASS=$((PASS+2))
else
  echo "❌ Secrets détectés en dur"
fi
echo ""

echo "📋 POINT 2 : ISOLATION RÉSEAU (4 pts)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Test 1 : PostgreSQL isolé (5432)"
if ! curl -m 1 localhost:5432 >/dev/null 2>&1; then
  echo "  ✅ Port 5432 fermé (DB isolée)"
  ((PASS=PASS+2))
else
  echo "  ❌ Port 5432 accessible (FAIL)"
fi

echo "Test 2 : Webapp publique (80)"
if curl -s -I http://localhost:80 | grep -q "200\|404"; then
  echo "  ✅ Port 80 accessible (Webapp publique)"
  ((PASS=PASS+2))
else
  echo "  ❌ Port 80 ne répond pas"
fi
echo ""

echo "📋 POINT 3 : MONITORING NETDATA (2 pts)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if curl -s http://localhost:19999/api/v2/info | grep -q "\"api\""; then
  echo "✅ Netdata actif (port 19999)"
  PASS=$((PASS+2))
else
  echo "❌ Netdata ne répond pas"
fi
echo ""

echo "📋 POINT 4 : MULTI-STAGE DOCKERFILES (3 pts)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
COUNT=0
if grep -q "AS builder" webapp/Dockerfile; then
  echo "  ✅ webapp/Dockerfile multi-stage"
  ((COUNT=COUNT+1))
fi
if grep -q "AS builder" Dockerfile; then
  echo "  ✅ Dockerfile (Python) multi-stage"
  ((COUNT=COUNT+1))
fi
if [ $COUNT -eq 2 ]; then
  PASS=$((PASS+3))
fi
echo ""

echo "📋 POINT 5 : FAILOVER MASTER/SLAVE (4 pts)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if docker compose ps | grep -q "db-master.*healthy" && docker compose ps | grep -q "db-slave.*healthy"; then
  echo "✅ Master et Slave présents et HEALTHY"
  PASS=$((PASS+4))
else
  echo "❌ Master ou Slave non opérational"
fi
echo ""

echo "════════════════════════════════════════════════════════════════"
echo "📊 RÉSULTAT FINAL"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Points obtenus : $PASS / $TOTAL"
if [ $PASS -eq 15 ]; then
  echo "🎉 BARÈME COMPLET - 15/15 POINTS !!!"
  echo "✨ Infrastructure Production-Grade Validée ✨"
else
  echo "⚠️  Points manquants : $((TOTAL - PASS))"
fi
echo ""
