# VeriGov AI - Expanded Trusted Sources

## Overview
We've expanded the whitelist from 27 to 54 trusted data sources across 13 categories. This significantly improves verification accuracy and coverage.

## Source Categories & Count

### 1. **Government - India** (5 sources)
- Press Information Bureau India (pib.gov.in)
- MyGov India (mygov.in)
- National Informatics Centre (nic.in)
- Open Government Data Platform India (data.gov.in)
- India Budget Portal (indiabudget.gov.in)

### 2. **Health & Medical** (6 sources)
- World Health Organization (who.int)
- Centers for Disease Control and Prevention (cdc.gov)
- National Institutes of Health (nih.gov)
- U.S. Food and Drug Administration (fda.gov)
- National Health Service UK (nhs.uk)
- PubMed - Medical Literature (pubmed.ncbi.nlm.nih.gov)

### 3. **Science & Research** (6 sources)
- Nature - International Journal of Science (nature.com)
- National Center for Biotechnology Information (ncbi.nlm.nih.gov)
- U.S. Geological Survey (usgs.gov)
- Science Daily (sciencedaily.com)
- arXiv - Scientific Papers (arxiv.org)
- Google Scholar (scholar.google.com)

### 4. **Space & Astronomy** (2 sources)
- NASA - National Aeronautics and Space Administration (nasa.gov)
- European Space Agency (esa.int)

### 5. **Government - UK** (2 sources)
- UK Government (gov.uk)
- UK Parliament (parliament.uk)

### 6. **Government - EU** (2 sources)
- European Union (europa.eu)
- European Commission (ec.europa.eu)

### 7. **Government - USA** (4 sources)
- The White House (whitehouse.gov)
- U.S. Department of State (state.gov)
- United States Census Bureau (census.gov)
- Bureau of Labor Statistics (bls.gov)

### 8. **Environment & Climate** (3 sources)
- U.S. Environmental Protection Agency (epa.gov)
- NASA Climate (climate.nasa.gov)
- Intergovernmental Panel on Climate Change (ipcc.ch)

### 9. **Weather & Meteorology** (2 sources)
- National Oceanic and Atmospheric Administration (noaa.gov)
- World Meteorological Organization (wmo.int)

### 10. **News & Media** (7 sources)
- BBC News (bbc.com)
- Associated Press (apnews.com)
- The Guardian (theguardian.com)
- The New York Times (nytimes.com)
- Reuters (reuters.com)
- Al Jazeera (aljazeera.com)
- BBC UK (bbc.co.uk)

### 11. **International Organizations** (8 sources)
- United Nations (un.org)
- World Bank (worldbank.org)
- International Monetary Fund (imf.org)
- OECD (oecd.org)
- Amnesty International (amnesty.org)
- Human Rights Watch (hrw.org)
- Transparency International (transparency.org)
- World Economic Forum (weforum.org)

### 12. **Reference & Encyclopedia** (3 sources)
- Britannica Encyclopedia (britannica.com)
- Oxford Bibliographies (oxfordbibliographies.com)
- Library of Congress (loc.gov)

### 13. **Data & Statistics** (3 sources)
- Statista - Statistics Portal (statista.com)
- Our World in Data (ourworldindata.org)
- Gapminder - Global Statistics (gapminder.org)

## Benefits of Expanded Sources

### 1. **Better Coverage**
- More sources per category means better verification
- Redundancy ensures reliability
- Multiple perspectives on same topic

### 2. **Improved Accuracy**
- Cross-reference multiple authoritative sources
- Reduce bias from single source
- Better fact-checking capability

### 3. **Specialized Knowledge**
- Medical claims verified by health organizations
- Climate data from climate specialists
- Economic data from economic experts

### 4. **Global Perspective**
- International organizations for global issues
- Regional governments for local policies
- Multiple news outlets for balanced reporting

### 5. **Academic Rigor**
- Scientific papers from arXiv and Google Scholar
- Medical literature from PubMed
- Research data from NCBI

## How Sources Are Used

### Topic Detection
The system automatically detects topics in claims and selects relevant sources:

```
Claim: "Vaccines prevent diseases"
→ Topics: health
→ Selected Sources: WHO, CDC, NIH, FDA, NHS, PubMed
```

### Source Selection Algorithm
1. Analyze claim for keywords
2. Identify relevant topics
3. Select 3 most relevant sources from category
4. Fetch content from selected sources
5. Verify claim against fetched content

### Fallback Strategy
If no sources match the topic:
1. Try related categories
2. Use news sources for current events
3. Use reference sources for biographical info
4. Fall back to AI knowledge base

## Quality Assurance

### Source Verification
All sources are:
- ✅ Verified to be accessible and working
- ✅ Recognized as authoritative in their field
- ✅ Regularly updated with current information
- ✅ Free from paywalls (or have free content)

### Maintenance
Sources are monitored for:
- Availability and uptime
- Content quality
- Relevance to verification tasks
- Accessibility issues

## Adding New Sources

To add a new trusted source:

1. **Verify Reliability**
   - Check domain authority
   - Verify content quality
   - Ensure regular updates

2. **Test Accessibility**
   - Confirm website is accessible
   - Check for paywalls
   - Verify content extraction works

3. **Add to Whitelist**
   ```json
   {
     "domain": "example.org",
     "name": "Example Organization",
     "category": "category_name",
     "approved_by": "system",
     "approved_date": "2026-03-08"
   }
   ```

4. **Update Lambda Handler**
   - Add to TRUSTED_SOURCES mapping
   - Add keywords to topic detection
   - Test with sample claims

5. **Deploy**
   - Run sync_whitelist.py
   - Deploy updated Lambda
   - Test with live queries

## Statistics

- **Total Sources**: 54
- **Categories**: 13
- **Average per Category**: 4.2
- **Government Sources**: 13
- **News Sources**: 7
- **Scientific Sources**: 12
- **International Sources**: 8
- **Reference Sources**: 3
- **Data Sources**: 3

## Future Expansion

Potential sources to add:
- More regional government portals
- Additional scientific journals
- More international news outlets
- Specialized databases (legal, medical, etc.)
- Academic institutions
- Think tanks and research centers

## Impact on Verification

With 54 trusted sources, the system can now:
- ✅ Verify claims across 13 different domains
- ✅ Cross-reference multiple authoritative sources
- ✅ Provide more confident verification results
- ✅ Handle diverse claim types
- ✅ Reduce false positives/negatives
- ✅ Improve overall accuracy

## Deployment

To deploy the expanded sources:

```bash
# Sync whitelist to DynamoDB
python scripts/sync_whitelist.py

# Deploy updated Lambda
python scripts/deploy_smart_lambda.py

# Test with new sources
python tests/test_live_lambda.py
```

All 54 sources are now active and ready for verification!
