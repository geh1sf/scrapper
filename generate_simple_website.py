#!/usr/bin/env python3
"""
Generate simple daily website - apartments and houses only
"""

import json
import os
from datetime import datetime, timedelta
import glob

def load_daily_results():
    """Load daily tracking results"""
    try:
        with open('data/daily_kraimorie_results.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {
            'timestamp': '',
            'total_current_properties': 0,
            'new_properties_today': 0,
            'argosdom_properties': 0,
            'new_properties': [],
            'all_argosdom_properties': [],
            'summary': {}
        }

def categorize_properties(properties):
    """Categorize properties - apartments and houses only"""
    apartments = []
    houses = []

    for prop in properties:
        title = prop.get('title', '').lower()
        if any(word in title for word in ['апартамент', 'студио', 'стая']):
            apartments.append(prop)
        else:  # Everything else goes to houses
            houses.append(prop)

    return apartments, houses

def generate_property_section(title, properties, color="#3498db"):
    """Generate HTML section for properties"""
    if not properties:
        return ""

    html = f"""
    <div class="section">
        <h2 style="color: {color}; border-bottom: 3px solid {color};">{title} ({len(properties)})</h2>
        <div class="properties-grid">
    """

    for i, prop in enumerate(properties, 1):
        argosdom_badge = '<span class="argosdom-badge">ARGOSDOM!</span>' if prop.get('is_argosdom') else ''
        vip_badge = '<span class="vip-badge">VIP</span>' if prop.get('listing_type') == 'vip' else ''

        image_html = ""
        if prop.get('image_url'):
            image_html = f'<div class="property-image"><img src="{prop.get("image_url")}" alt="Property" loading="lazy"></div>'

        html += f"""
        <div class="property-card">
            <div class="property-header">
                <h3>Property #{i} {argosdom_badge} {vip_badge}</h3>
            </div>
            {image_html}
            <div class="property-content">
                <h4>{prop.get('title', 'No title')}</h4>
                <div class="detail-row"><strong>Price:</strong> {prop.get('price', 'Not specified')}</div>
                <div class="detail-row"><strong>Location:</strong> {prop.get('location', 'Not specified')}</div>
                <a href="{prop.get('url', '#')}" target="_blank" class="view-btn">View on alo.bg</a>
            </div>
        </div>
        """

    html += "</div></div>"
    return html

def get_archive_files():
    """Get list of available archive files"""
    archive_files = []
    if os.path.exists('docs/archive'):
        for file in sorted(glob.glob('docs/archive/????-??-??.html'), reverse=True):
            date_str = os.path.basename(file).replace('.html', '')
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                archive_files.append({
                    'date': date_str,
                    'display': date_obj.strftime('%B %d, %Y'),
                    'file': f'archive/{date_str}.html'
                })
            except:
                pass
    return archive_files[:30]  # Keep last 30 days

def generate_navigation():
    """Generate navigation menu"""
    archive_files = get_archive_files()

    nav_html = """
        <div class="navigation">
            <div class="nav-container">
                <a href="index.html" class="nav-item active">📅 Today's Properties</a>
    """

    if archive_files:
        nav_html += '<div class="dropdown"><button class="dropbtn">📚 Previous Days ▼</button><div class="dropdown-content">'

        for archive in archive_files:
            nav_html += f'<a href="{archive["file"]}">{archive["display"]}</a>'

        nav_html += '</div></div>'

    nav_html += "</div></div>"
    return nav_html

def generate_archive_page(date_str, results, apartments, houses, argosdom_apartments, argosdom_houses):
    """Generate archive page for a specific date"""

    # Parse timestamp
    timestamp = results.get('timestamp', '')
    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_time = dt.strftime('%Y-%m-%d %H:%M UTC')
            display_date = dt.strftime('%B %d, %Y')
        except:
            formatted_time = timestamp
            display_date = date_str
    else:
        formatted_time = 'Unknown'
        display_date = date_str

    total_new = len(apartments) + len(houses)
    total_argosdom = len(argosdom_apartments) + len(argosdom_houses)

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kraimorie Properties - {display_date}</title>
    <style>
        body {{ font-family: 'Segoe UI', system-ui, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 30px; text-align: center; }}
        .header h1 {{ margin: 0; color: #2c3e50; }}
        .header .subtitle {{ color: #7f8c8d; margin: 10px 0; }}

        .navigation {{ background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .nav-container {{ display: flex; align-items: center; padding: 10px; gap: 10px; flex-wrap: wrap; }}
        .nav-item {{ padding: 10px 20px; border-radius: 6px; text-decoration: none; color: #666; background: #f8f9fa; }}
        .nav-item.active {{ background: #3498db; color: white; }}

        .dropdown {{ position: relative; }}
        .dropbtn {{ padding: 10px 20px; border: none; border-radius: 6px; background: #95a5a6; color: white; cursor: pointer; }}
        .dropdown-content {{ display: none; position: absolute; background: white; min-width: 200px; box-shadow: 0 8px 16px rgba(0,0,0,0.2); z-index: 1; border-radius: 4px; max-height: 300px; overflow-y: auto; }}
        .dropdown-content a {{ color: #333; padding: 12px 16px; text-decoration: none; display: block; }}
        .dropdown-content a:hover {{ background: #f1f1f1; }}
        .dropdown:hover .dropdown-content {{ display: block; }}

        .status {{ padding: 20px; border-radius: 8px; margin: 20px 0; font-weight: bold; text-align: center; background: #e8f5e8; color: #2d5d2d; }}

        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #3498db; }}
        .stat-label {{ color: #7f8c8d; }}

        .section {{ margin: 30px 0; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .properties-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 20px; margin: 20px 0; }}
        .property-card {{ background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; overflow: hidden; }}
        .property-header {{ background: #3498db; color: white; padding: 15px; }}
        .property-header h3 {{ margin: 0; font-size: 1.1em; }}
        .property-image {{ width: 100%; height: 200px; overflow: hidden; }}
        .property-image img {{ width: 100%; height: 100%; object-fit: cover; }}
        .property-content {{ padding: 15px; }}
        .property-content h4 {{ margin: 0 0 10px 0; color: #2c3e50; }}
        .detail-row {{ margin: 5px 0; color: #666; }}
        .view-btn {{ display: inline-block; background: #27ae60; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; margin-top: 10px; }}

        .argosdom-badge {{ background: #e74c3c; color: white; padding: 3px 8px; border-radius: 3px; font-size: 0.8em; margin-left: 5px; }}
        .vip-badge {{ background: #f39c12; color: white; padding: 3px 8px; border-radius: 3px; font-size: 0.8em; margin-left: 5px; }}

        .footer {{ text-align: center; margin: 40px 0; color: #7f8c8d; }}

        @media (max-width: 768px) {{
            .properties-grid {{ grid-template-columns: 1fr; }}
            .stats {{ grid-template-columns: repeat(2, 1fr); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Kraimorie Properties - {display_date}</h1>
            <div class="subtitle">Properties found on {display_date}</div>
            <div class="subtitle">Scan time: {formatted_time}</div>
        </div>

        <div class="navigation">
            <div class="nav-container">
                <a href="../index.html" class="nav-item">📅 Today's Properties</a>
                <span style="color: #3498db; font-weight: bold;">📚 Archive: {display_date}</span>
            </div>
        </div>

        <div class="status">
            Found {total_new} new properties on {display_date}
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{len(apartments)}</div>
                <div class="stat-label">New Apartments</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(houses)}</div>
                <div class="stat-label">New Houses</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{results.get('total_current_properties', 0)}</div>
                <div class="stat-label">Total Available</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{total_argosdom}</div>
                <div class="stat-label">Argosdom Properties</div>
            </div>
        </div>
"""

    # Add sections
    if apartments:
        html += generate_property_section("🏠 APARTMENTS FOUND", apartments, "#e74c3c")

    if houses:
        html += generate_property_section("🏡 HOUSES FOUND", houses, "#e74c3c")

    if argosdom_apartments:
        html += generate_property_section("⭐ ARGOSDOM APARTMENTS", argosdom_apartments, "#9b59b6")

    if argosdom_houses:
        html += generate_property_section("⭐ ARGOSDOM HOUSES", argosdom_houses, "#9b59b6")

    if not total_new:
        html += '<div class="section"><h2 style="text-align: center; color: #666;">No new properties found on this day</h2></div>'

    html += f"""
        <div class="footer">
            <p>📅 Archive from {display_date}</p>
            <p>🤖 Kraimorie Property Tracker</p>
        </div>
    </div>
</body>
</html>
"""

    return html

def cleanup_old_archives():
    """Remove archive files older than 30 days"""
    cutoff_date = datetime.now() - timedelta(days=30)

    if os.path.exists('docs/archive'):
        for file in glob.glob('docs/archive/????-??-??.html'):
            try:
                file_date_str = os.path.basename(file).replace('.html', '')
                file_date = datetime.strptime(file_date_str, '%Y-%m-%d')

                if file_date < cutoff_date:
                    os.remove(file)
                    print(f"Removed old archive: {file}")
            except:
                pass

def generate_website():
    """Generate the website"""
    results = load_daily_results()

    # Parse timestamp
    timestamp = results.get('timestamp', '')
    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            formatted_time = dt.strftime('%Y-%m-%d %H:%M UTC')
        except:
            formatted_time = timestamp
    else:
        formatted_time = 'Unknown'

    # Get data
    new_properties = results.get('new_properties', [])
    argosdom_properties = results.get('all_argosdom_properties', [])

    # Split by type
    new_apartments, new_houses = categorize_properties(new_properties)
    argosdom_apartments, argosdom_houses = categorize_properties(argosdom_properties)

    # Status
    if new_properties:
        status_class = 'success'
        status_text = f"Found {len(new_properties)} new properties today"
    else:
        status_class = 'no-results'
        status_text = "No new properties today"

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kraimorie Daily Properties</title>
    <style>
        body {{ font-family: 'Segoe UI', system-ui, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 30px; text-align: center; }}
        .header h1 {{ margin: 0; color: #2c3e50; }}
        .header .subtitle {{ color: #7f8c8d; margin: 10px 0; }}

        .navigation {{ background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .nav-container {{ display: flex; align-items: center; padding: 10px; gap: 10px; flex-wrap: wrap; }}
        .nav-item {{ padding: 10px 20px; border-radius: 6px; text-decoration: none; color: #666; background: #f8f9fa; }}
        .nav-item.active {{ background: #3498db; color: white; }}

        .dropdown {{ position: relative; }}
        .dropbtn {{ padding: 10px 20px; border: none; border-radius: 6px; background: #95a5a6; color: white; cursor: pointer; }}
        .dropdown-content {{ display: none; position: absolute; background: white; min-width: 200px; box-shadow: 0 8px 16px rgba(0,0,0,0.2); z-index: 1; border-radius: 4px; max-height: 300px; overflow-y: auto; }}
        .dropdown-content a {{ color: #333; padding: 12px 16px; text-decoration: none; display: block; }}
        .dropdown-content a:hover {{ background: #f1f1f1; }}
        .dropdown:hover .dropdown-content {{ display: block; }}

        .status {{ padding: 20px; border-radius: 8px; margin: 20px 0; font-weight: bold; text-align: center; }}
        .status.success {{ background: #d4edda; color: #155724; }}
        .status.no-results {{ background: #d1ecf1; color: #0c5460; }}

        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }}
        .stat-number {{ font-size: 2em; font-weight: bold; color: #3498db; }}
        .stat-label {{ color: #7f8c8d; }}

        .section {{ margin: 30px 0; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .properties-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 20px; margin: 20px 0; }}
        .property-card {{ background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; overflow: hidden; }}
        .property-header {{ background: #3498db; color: white; padding: 15px; }}
        .property-header h3 {{ margin: 0; font-size: 1.1em; }}
        .property-image {{ width: 100%; height: 200px; overflow: hidden; }}
        .property-image img {{ width: 100%; height: 100%; object-fit: cover; }}
        .property-content {{ padding: 15px; }}
        .property-content h4 {{ margin: 0 0 10px 0; color: #2c3e50; }}
        .detail-row {{ margin: 5px 0; color: #666; }}
        .view-btn {{ display: inline-block; background: #27ae60; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; margin-top: 10px; }}
        .view-btn:hover {{ background: #229954; }}

        .argosdom-badge {{ background: #e74c3c; color: white; padding: 3px 8px; border-radius: 3px; font-size: 0.8em; margin-left: 5px; }}
        .vip-badge {{ background: #f39c12; color: white; padding: 3px 8px; border-radius: 3px; font-size: 0.8em; margin-left: 5px; }}

        .footer {{ text-align: center; margin: 40px 0; color: #7f8c8d; }}

        @media (max-width: 768px) {{
            .properties-grid {{ grid-template-columns: 1fr; }}
            .stats {{ grid-template-columns: repeat(2, 1fr); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Kraimorie Daily Properties</h1>
            <div class="subtitle">Apartments and Houses in Kraimorie, Burgas</div>
            <div class="subtitle">Last updated: {formatted_time}</div>
        </div>

        <div class="status {status_class}">
            {status_text}
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{len(new_apartments)}</div>
                <div class="stat-label">New Apartments</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(new_houses)}</div>
                <div class="stat-label">New Houses</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{results.get('total_current_properties', 0)}</div>
                <div class="stat-label">Total Available</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(argosdom_properties)}</div>
                <div class="stat-label">Argosdom Properties</div>
            </div>
        </div>
"""

    # Add sections only if they have content
    if new_apartments:
        html += generate_property_section("🏠 NEW APARTMENTS TODAY", new_apartments, "#e74c3c")

    if new_houses:
        html += generate_property_section("🏡 NEW HOUSES TODAY", new_houses, "#e74c3c")

    if argosdom_apartments:
        html += generate_property_section("⭐ ARGOSDOM APARTMENTS", argosdom_apartments, "#9b59b6")

    if argosdom_houses:
        html += generate_property_section("⭐ ARGOSDOM HOUSES", argosdom_houses, "#9b59b6")

    if not new_properties:
        html += '<div class="section"><h2 style="text-align: center; color: #666;">No new properties today</h2></div>'

    html += f"""
        {generate_navigation()}

        <div class="footer">
            <p>🔄 Updates daily at 23:57 UTC • Apartments and Houses only</p>
            <p>📅 Previous days available in menu above</p>
            <p>🤖 Kraimorie Property Tracker</p>
        </div>
    </div>
</body>
</html>
"""

    # Save main website
    os.makedirs('docs', exist_ok=True)
    os.makedirs('docs/archive', exist_ok=True)
    with open('docs/index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    # Create archive page for today (if there are new properties)
    if new_properties or argosdom_properties:
        today = datetime.now().strftime('%Y-%m-%d')
        archive_html = generate_archive_page(today, results, new_apartments, new_houses, argosdom_apartments, argosdom_houses)
        with open(f'docs/archive/{today}.html', 'w', encoding='utf-8') as f:
            f.write(archive_html)

    # Clean up old archives (keep only 30 days)
    cleanup_old_archives()

    with open('docs/.nojekyll', 'w') as f:
        f.write('')

    print("Simple website with archives generated successfully!")

if __name__ == "__main__":
    generate_website()