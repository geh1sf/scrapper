#!/usr/bin/env python3
"""
Generate GitHub Pages website from scraping results
"""

import json
import os
from datetime import datetime
from typing import List, Dict

def load_results():
    """Load latest results and history"""
    try:
        with open('data/latest_results.json', 'r', encoding='utf-8') as f:
            latest = json.load(f)
    except:
        latest = {'new_properties': [], 'timestamp': '', 'stats': {}}

    try:
        with open('data/scraping_history.json', 'r', encoding='utf-8') as f:
            history = json.load(f)
    except:
        history = []

    return latest, history

def group_properties_by_type(properties: List[Dict]) -> Dict[str, List[Dict]]:
    """Group properties by broker and type"""
    grouped = {
        'argosdom_houses': [],
        'argosdom_apartments': [],
        'other_houses': [],
        'other_apartments': []
    }

    for prop in properties:
        lister = prop.get('lister', '').lower()
        title = prop.get('title', '').lower()
        search_city = prop.get('search_city', '').lower()

        # Check if it's from Argosdom
        is_argosdom = any(keyword in lister for keyword in ['argosdom', 'argos'])

        # Check if it's a house or apartment
        is_house = any(keyword in title or keyword in search_city for keyword in [
            'къща', 'вила', 'house', 'villa', 'houses'
        ])

        # Categorize
        if is_argosdom and is_house:
            grouped['argosdom_houses'].append(prop)
        elif is_argosdom:
            grouped['argosdom_apartments'].append(prop)
        elif is_house:
            grouped['other_houses'].append(prop)
        else:
            grouped['other_apartments'].append(prop)

    return grouped

def generate_property_section(title: str, properties: List[Dict], emoji: str = "🏠") -> str:
    """Generate HTML for a property section"""
    if not properties:
        return f"""
        <div class="property-section">
            <h2 class="section-title">{emoji} {title} <span class="section-count">(0)</span></h2>
            <div class="no-properties">No properties found in this category.</div>
        </div>
        """

    html = f"""
    <div class="property-section">
        <h2 class="section-title">{emoji} {title} <span class="section-count">({len(properties)})</span></h2>
        <div class="properties-grid">
    """

    for i, prop in enumerate(properties, 1):
        lister_info = f"<div class='info-item'><strong>👤 Listed by:</strong> {prop.get('lister', 'Not specified')}</div>" if prop.get('lister') else ""

        html += f"""
        <div class="property-card">
            <div class="property-header">
                <h3>🏠 Property #{i}</h3>
                <div class="property-price">{prop.get('price', 'Price not available')}</div>
            </div>
            <div class="property-details">
                <h4>{prop.get('title', 'No title')}</h4>
                <div class="property-info">
                    <span class="info-item">📍 {prop.get('location', 'Location not specified')}</span>
                    <span class="info-item">📐 {prop.get('area', 'Area not specified')}</span>
                    <span class="info-item">🏢 {prop.get('floor', 'Floor not specified')}</span>
                    <span class="info-item">🏙️ {prop.get('search_city', 'Not specified')}</span>
                    {lister_info}
                </div>
                <div class="property-actions">
                    <a href="{prop.get('url', '#')}" target="_blank" class="view-property">View Property on alo.bg</a>
                </div>
            </div>
        </div>
        """

    html += """
        </div>
    </div>
    """

    return html

def generate_organized_properties(properties: List[Dict]) -> str:
    """Generate organized HTML for all properties"""
    if not properties:
        return '<div class="no-properties">🏠 No new properties found in the latest scan.</div>'

    grouped = group_properties_by_type(properties)

    html = ""

    # Section 1: Argosdom Houses
    html += generate_property_section(
        "Argosdom Houses",
        grouped['argosdom_houses'],
        "🏡"
    )

    # Section 2: Argosdom Apartments
    html += generate_property_section(
        "Argosdom Apartments",
        grouped['argosdom_apartments'],
        "🏢"
    )

    # Section 3: Other Houses
    html += generate_property_section(
        "Other Agency Houses",
        grouped['other_houses'],
        "🏠"
    )

    # Section 4: Other Apartments
    html += generate_property_section(
        "Other Agency Apartments",
        grouped['other_apartments'],
        "🏘️"
    )

    return html

def generate_history_chart(history: List[Dict]) -> str:
    """Generate simple history chart"""
    if not history:
        return "<p>No history available</p>"

    chart_data = []
    for entry in history[-14:]:  # Last 14 days
        date = entry['date']
        count = entry['new_count']
        chart_data.append(f"['{date}', {count}]")

    return f"""
    <div id="history-chart">
        <h3>📊 Last 14 Days Activity</h3>
        <div class="chart-container">
            {', '.join([f"<div class='chart-bar' style='height: {max(h['new_count']*10, 5)}px' title='{h['date']}: {h['new_count']} properties'></div>" for h in history[-14:]])}
        </div>
    </div>
    """

def generate_website():
    """Generate complete website"""
    latest, history = load_results()

    # Get data
    properties = latest.get('new_properties', [])
    timestamp = latest.get('timestamp', '')
    stats = latest.get('stats', {})
    error = latest.get('error')

    # Parse timestamp
    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_time = dt.strftime('%Y-%m-%d %H:%M UTC')
        except:
            formatted_time = timestamp
    else:
        formatted_time = 'Unknown'

    # Status
    status_class = 'error' if error else ('success' if properties else 'no-results')
    status_text = error if error else (f"Found {len(properties)} new properties" if properties else "No new properties")

    # Generate HTML
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏠 Sofia Property Scraper</title>
    <style>
        body {{ font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 30px; text-align: center; }}
        .header h1 {{ margin: 0; color: #2c3e50; font-size: 2.5em; }}
        .header .subtitle {{ color: #7f8c8d; margin: 10px 0; }}

        .status {{ padding: 20px; border-radius: 8px; margin: 20px 0; font-weight: bold; }}
        .status.success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .status.error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
        .status.no-results {{ background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}

        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #3498db; }}
        .stat-label {{ color: #7f8c8d; margin-top: 5px; }}

        .property-section {{ margin: 40px 0; }}
        .section-title {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; margin-bottom: 30px; }}
        .section-count {{ color: #7f8c8d; font-weight: normal; }}
        .properties-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 20px; margin: 20px 0; }}
        .property-card {{ background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.2s; }}
        .property-card:hover {{ transform: translateY(-2px); }}
        .property-header {{ background: #3498db; color: white; padding: 20px; }}
        .property-header h3 {{ margin: 0; font-size: 1.2em; }}
        .property-price {{ font-size: 1.4em; font-weight: bold; margin-top: 8px; }}
        .property-details {{ padding: 20px; }}
        .property-details h4 {{ margin: 0 0 15px 0; color: #2c3e50; }}
        .property-info {{ margin: 15px 0; }}
        .info-item {{ display: block; margin: 8px 0; color: #666; }}
        .view-property {{ display: inline-block; background: #27ae60; color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px; margin-top: 15px; }}
        .view-property:hover {{ background: #229954; }}

        .no-properties {{ text-align: center; padding: 60px 20px; background: white; border-radius: 12px; color: #7f8c8d; font-size: 1.2em; }}

        .footer {{ text-align: center; margin: 40px 0; color: #7f8c8d; }}
        .chart-container {{ display: flex; align-items: end; justify-content: space-between; height: 100px; margin: 20px 0; }}
        .chart-bar {{ background: #3498db; min-width: 20px; margin: 0 2px; border-radius: 4px 4px 0 0; }}

        @media (max-width: 768px) {{
            .properties-grid {{ grid-template-columns: 1fr; }}
            .stats {{ grid-template-columns: repeat(2, 1fr); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏠 Sofia Property Scraper</h1>
            <div class="subtitle">Automated apartment hunting in Sofia, Bulgaria</div>
            <div class="subtitle">Last updated: {formatted_time}</div>
        </div>

        <div class="status {status_class}">
            📊 Status: {status_text}
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{len(properties)}</div>
                <div class="stat-label">New Properties</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{latest.get('total_properties_scanned', 0)}</div>
                <div class="stat-label">Total Scanned</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats.get('total_properties_seen', 0)}</div>
                <div class="stat-label">All Time Tracked</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(history)}</div>
                <div class="stat-label">Days Active</div>
            </div>
        </div>

        {generate_history_chart(history)}

        {generate_organized_properties(properties)}

        <div class="footer">
            <p>🤖 Powered by GitHub Actions • 🔄 Updates daily at 8:00 AM UTC</p>
            <p>🏠 Searching for apartments in Sofia, Bulgaria via alo.bg</p>
        </div>
    </div>
</body>
</html>
"""

    # Save website
    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    # Disable Jekyll processing
    with open('docs/.nojekyll', 'w') as f:
        f.write('')

    print("🌐 Website generated successfully!")

if __name__ == "__main__":
    generate_website()