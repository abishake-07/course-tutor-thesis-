#!/usr/bin/env python3
"""Generate an interactive HTML dashboard summarizing RQ1 baseline evaluation results."""
import json
import webbrowser
from pathlib import Path

def load_json(path):
    """Load JSON file with fallback to non-prefixed variant."""
    p = Path(path)
    if not p.exists():
        # Try non-prefixed variant
        alt = p.parent / p.name.replace(p.name.split('_')[0] + '_', '')
        if alt.exists():
            p = alt
    with open(p, 'r') as f:
        return json.load(f)

def build_dashboard():
    """Load results and generate dashboard HTML."""

    # Load all JSON files
    phi_eval = load_json('results/phi-mini/baseline/phi_evaluation_report.json')
    phi_attack = load_json('results/phi-mini/baseline/phi_attack_success_analysis.json')
    phi_mode = load_json('results/phi-mini/baseline/phi_asr_by_failure_mode.json')

    llama_eval = load_json('results/llama/baseline/llama_evaluation_report.json')
    llama_attack = load_json('results/llama/baseline/llama_attack_success_analysis.json')
    llama_mode = load_json('results/llama/baseline/llama_asr_by_failure_mode.json')

    # Extract KPIs
    phi_asr = phi_attack['asr_statistics']['overall_asr']
    llama_asr = llama_attack['asr_statistics']['overall_asr']
    phi_fpr = phi_eval['summary']['benign_queries']['false_positive_rate']
    llama_fpr = llama_eval['summary']['benign_queries']['false_positive_rate']

    # Extract per-category ASR
    phi_by_cat = phi_attack['asr_statistics']['by_category']
    llama_by_cat = llama_attack['asr_statistics']['by_category']
    categories = sorted(phi_by_cat.keys())

    phi_cat_asr = [phi_by_cat[c]['asr'] for c in categories]
    llama_cat_asr = [llama_by_cat[c]['asr'] for c in categories]

    # Extract outcome distribution
    phi_outcomes = phi_attack['asr_statistics']['by_outcome']
    llama_outcomes = llama_attack['asr_statistics']['by_outcome']

    # Build severity distribution (count by severity and success for each category)
    def extract_severity_by_category(attack_data):
        """Returns dict: category -> {severity -> {total, successful}}"""
        severity_by_cat = {}
        for attack in attack_data['attack_analyses']:
            cat = attack['attack_category']
            severity = attack['severity']
            success = attack['attack_succeeded']

            if cat not in severity_by_cat:
                severity_by_cat[cat] = {
                    'medium': {'total': 0, 'successful': 0},
                    'high': {'total': 0, 'successful': 0},
                    'critical': {'total': 0, 'successful': 0}
                }

            severity_by_cat[cat][severity]['total'] += 1
            if success:
                severity_by_cat[cat][severity]['successful'] += 1

        return severity_by_cat

    phi_severity = extract_severity_by_category(phi_attack)
    llama_severity = extract_severity_by_category(llama_attack)

    # Failure mode heatmap data (from asr_by_failure_mode)
    phi_cat_mode = phi_mode['asr_by_mode']['category_mode_stats']
    llama_cat_mode = llama_mode['asr_by_mode']['category_mode_stats']

    # Overall metrics for comparison
    phi_detection = phi_eval['summary']['attack_queries']['detection_rate']
    llama_detection = llama_eval['summary']['attack_queries']['detection_rate']
    phi_accuracy = phi_eval['summary']['overall_accuracy']['accuracy']
    llama_accuracy = llama_eval['summary']['overall_accuracy']['accuracy']

    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RQ1 Baseline Evaluation Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-2.35.0.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', sans-serif;
            background: #0f1419;
            color: #e0e0e0;
            padding: 2rem;
        }}

        .container {{
            max-width: 1600px;
            margin: 0 auto;
        }}

        h1 {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
            color: #fff;
        }}

        .subtitle {{
            font-size: 0.95rem;
            color: #a0a0a0;
            margin-bottom: 2rem;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .kpi {{
            background: #1a1f2e;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 1.5rem;
            text-align: center;
        }}

        .kpi-value {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #4a9eff;
            margin: 0.5rem 0;
        }}

        .kpi-label {{
            font-size: 0.85rem;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .chart-container {{
            background: #1a1f2e;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }}

        .chart-title {{
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #fff;
        }}

        .chart {{
            width: 100%;
            height: 400px;
        }}

        .grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        @media (max-width: 1024px) {{
            .grid-2 {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>RQ1 Baseline Evaluation Results</h1>
        <p class="subtitle">Attack Success Rate & Defense Analysis — phi-mini vs llama</p>

        <!-- KPI Cards -->
        <div class="grid" style="grid-template-columns: repeat(3, 1fr);">
            <div class="kpi">
                <div class="kpi-label">Phi-mini ASR</div>
                <div class="kpi-value">{phi_asr:.1f}%</div>
            </div>
            <div class="kpi">
                <div class="kpi-label">LLaMA ASR</div>
                <div class="kpi-value">{llama_asr:.1f}%</div>
            </div>
            <div class="kpi">
                <div class="kpi-label">Benign FPR</div>
                <div class="kpi-value">{phi_fpr:.1f}%</div>
            </div>
        </div>

        <!-- Overall Comparison -->
        <div class="chart-container">
            <div class="chart-title">Overall Metrics Comparison</div>
            <div class="chart" id="overall-comparison"></div>
        </div>

        <!-- Per-Category ASR -->
        <div class="chart-container">
            <div class="chart-title">Attack Success Rate by Category</div>
            <div class="chart" id="category-asr"></div>
        </div>

        <!-- Outcome Distribution -->
        <div class="grid-2">
            <div class="chart-container">
                <div class="chart-title">Outcome Distribution — Phi-mini</div>
                <div class="chart" id="outcome-phi"></div>
            </div>
            <div class="chart-container">
                <div class="chart-title">Outcome Distribution — LLaMA</div>
                <div class="chart" id="outcome-llama"></div>
            </div>
        </div>

        <!-- Severity Distribution -->
        <div class="chart-container">
            <div class="chart-title">Severity Distribution by Category</div>
            <div class="chart" id="severity-dist"></div>
        </div>
    </div>

    <script>
        const phi_asr = {phi_asr};
        const llama_asr = {llama_asr};
        const phi_detection = {phi_detection};
        const llama_detection = {llama_detection};
        const phi_accuracy = {phi_accuracy};
        const llama_accuracy = {llama_accuracy};

        const categories = {json.dumps(categories)};
        const phi_cat_asr = {json.dumps(phi_cat_asr)};
        const llama_cat_asr = {json.dumps(llama_cat_asr)};

        const phi_outcomes = {json.dumps(phi_outcomes)};
        const llama_outcomes = {json.dumps(llama_outcomes)};

        // Overall Comparison
        const overall_comp = {{
            data: [
                {{
                    name: 'Phi-mini',
                    x: ['ASR (%)', 'Detection Rate (%)', 'Accuracy (%)'],
                    y: [phi_asr, phi_detection, phi_accuracy],
                    type: 'bar',
                    marker: {{color: '#4a9eff'}}
                }},
                {{
                    name: 'LLaMA',
                    x: ['ASR (%)', 'Detection Rate (%)', 'Accuracy (%)'],
                    y: [llama_asr, llama_detection, llama_accuracy],
                    type: 'bar',
                    marker: {{color: '#ff6b6b'}}
                }}
            ],
            layout: {{
                barmode: 'group',
                plot_bgcolor: '#1a1f2e',
                paper_bgcolor: '#1a1f2e',
                font: {{color: '#e0e0e0'}},
                xaxis: {{gridcolor: '#333'}},
                yaxis: {{gridcolor: '#333'}},
                hovermode: 'closest'
            }}
        }};
        Plotly.newPlot('overall-comparison', overall_comp.data, overall_comp.layout, {{responsive: true}});

        // Category ASR
        const cat_asr = {{
            data: [
                {{
                    name: 'Phi-mini',
                    y: categories,
                    x: phi_cat_asr,
                    type: 'bar',
                    orientation: 'h',
                    marker: {{color: '#4a9eff'}}
                }},
                {{
                    name: 'LLaMA',
                    y: categories,
                    x: llama_cat_asr,
                    type: 'bar',
                    orientation: 'h',
                    marker: {{color: '#ff6b6b'}}
                }}
            ],
            layout: {{
                barmode: 'group',
                plot_bgcolor: '#1a1f2e',
                paper_bgcolor: '#1a1f2e',
                font: {{color: '#e0e0e0'}},
                xaxis: {{title: 'ASR (%)', gridcolor: '#333'}},
                hovermode: 'closest'
            }}
        }};
        Plotly.newPlot('category-asr', cat_asr.data, cat_asr.layout, {{responsive: true}});

        // Outcome Distribution - Phi
        const phi_out = phi_outcomes;
        const phi_labels = Object.keys(phi_out);
        const phi_values = Object.values(phi_out);

        const outcome_phi = {{
            data: [{{
                labels: phi_labels,
                values: phi_values,
                type: 'pie',
                hole: 0.4,
                marker: {{colors: ['#ffb347', '#90ee90', '#ff6b6b']}}
            }}],
            layout: {{
                plot_bgcolor: '#1a1f2e',
                paper_bgcolor: '#1a1f2e',
                font: {{color: '#e0e0e0'}}
            }}
        }};
        Plotly.newPlot('outcome-phi', outcome_phi.data, outcome_phi.layout, {{responsive: true}});

        // Outcome Distribution - LLaMA
        const llama_out = llama_outcomes;
        const llama_labels = Object.keys(llama_out);
        const llama_values = Object.values(llama_out);

        const outcome_llama = {{
            data: [{{
                labels: llama_labels,
                values: llama_values,
                type: 'pie',
                hole: 0.4,
                marker: {{colors: ['#ffb347', '#90ee90', '#ff6b6b']}}
            }}],
            layout: {{
                plot_bgcolor: '#1a1f2e',
                paper_bgcolor: '#1a1f2e',
                font: {{color: '#e0e0e0'}}
            }}
        }};
        Plotly.newPlot('outcome-llama', outcome_llama.data, outcome_llama.layout, {{responsive: true}});

        // Severity Distribution
        const phi_severity = {json.dumps(phi_severity)};
        const severity_data = [];
        const severity_cats = Object.keys(phi_severity);
        const severity_levels = ['medium', 'high', 'critical'];

        for (const sev of severity_levels) {{
            const counts = severity_cats.map(cat => phi_severity[cat][sev]['total'] || 0);
            severity_data.push({{
                name: sev.charAt(0).toUpperCase() + sev.slice(1),
                y: severity_cats,
                x: counts,
                type: 'bar',
                orientation: 'h'
            }});
        }}

        const severity_dist = {{
            data: severity_data,
            layout: {{
                barmode: 'stack',
                plot_bgcolor: '#1a1f2e',
                paper_bgcolor: '#1a1f2e',
                font: {{color: '#e0e0e0'}},
                xaxis: {{title: 'Count', gridcolor: '#333'}},
                hovermode: 'closest'
            }}
        }};
        Plotly.newPlot('severity-dist', severity_dist.data, severity_dist.layout, {{responsive: true}});
    </script>
</body>
</html>
"""

    output_path = Path('results/dashboard.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Dashboard written to {output_path}")
    print(f"Opening in browser...")
    webbrowser.open(f"file:///{output_path.resolve()}")

if __name__ == '__main__':
    build_dashboard()
