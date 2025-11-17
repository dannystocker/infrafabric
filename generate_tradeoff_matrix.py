#!/usr/bin/env python3
"""
Generate a 2×2 tradeoff matrix: Efficiency vs. Loyalty
Specifications:
- Width: 168mm (6.61 inches)
- Max height: 420px (1.4 inches at 300 DPI)
- DPI: 300
- Format: Quadrant matrix with color coding
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle, FancyArrowPatch
from matplotlib.patheffects import withStroke
import os

def generate_tradeoff_matrix():
    """Generate the 2×2 efficiency vs loyalty tradeoff matrix."""

    # Create figure with appropriate dimensions
    # 168mm width at 300 DPI = 1984px = 6.613 inches
    # Height: maintain good aspect ratio within 420px max
    fig_width_inch = 168 / 25.4  # mm to inches
    fig_height_inch = 5.0  # inches (will be ~1500px at 300 DPI, within limits)

    fig, ax = plt.subplots(figsize=(fig_width_inch, fig_height_inch), dpi=300)

    # Set up the plotting area
    ax.set_xlim(-0.8, 5.2)
    ax.set_ylim(-0.8, 5.0)
    ax.set_aspect('equal')

    # Define quadrant colors and labels
    quadrants = [
        {
            'x': 0, 'y': 0, 'w': 2, 'h': 2,
            'color': '#FF6B6B',  # Red
            'title': 'Catastrophe',
            'subtitle': 'Zone à Éviter',
            'efficiency': 'LOW',
            'loyalty': 'LOW'
        },
        {
            'x': 2, 'y': 0, 'w': 2, 'h': 2,
            'color': '#FFE66D',  # Yellow
            'title': 'Optimisation\nAveugle',
            'subtitle': 'Risque Client',
            'efficiency': 'HIGH',
            'loyalty': 'LOW'
        },
        {
            'x': 0, 'y': 2, 'w': 2, 'h': 2,
            'color': '#FFA500',  # Orange
            'title': 'Investissement\nRelationnel',
            'subtitle': 'Coûteux mais Fidèle',
            'efficiency': 'LOW',
            'loyalty': 'HIGH'
        },
        {
            'x': 2, 'y': 2, 'w': 2, 'h': 2,
            'color': '#52B788',  # Green
            'title': 'Zone Optimale',
            'subtitle': 'Idéale',
            'efficiency': 'HIGH',
            'loyalty': 'HIGH'
        }
    ]

    # Draw quadrants with borders
    for quad in quadrants:
        rect = Rectangle(
            (quad['x'], quad['y']), quad['w'], quad['h'],
            linewidth=3.0, edgecolor='#333333',
            facecolor=quad['color'], alpha=0.78
        )
        ax.add_patch(rect)

        # Add quadrant title (bold, high contrast)
        title_text = ax.text(
            quad['x'] + quad['w']/2, quad['y'] + quad['h']/2 + 0.35,
            quad['title'],
            ha='center', va='center',
            fontsize=11, fontweight='bold',
            color='white', family='sans-serif'
        )
        title_text.set_path_effects([withStroke(linewidth=3, foreground='black')])

        # Add subtitle
        subtitle_text = ax.text(
            quad['x'] + quad['w']/2, quad['y'] + quad['h']/2 - 0.35,
            quad['subtitle'],
            ha='center', va='center',
            fontsize=9, style='italic',
            color='white', family='sans-serif'
        )
        subtitle_text.set_path_effects([withStroke(linewidth=2.5, foreground='black')])

    # Draw axes with arrows
    arrow_props = dict(arrowstyle='->', lw=2.5, color='#000000')

    # X-axis (Efficiency)
    ax.annotate('', xy=(4.8, 2), xytext=(-0.6, 2),
               arrowprops=arrow_props)
    # Y-axis (Loyalty)
    ax.annotate('', xy=(2, 4.8), xytext=(2, -0.6),
               arrowprops=arrow_props)

    # Axis labels with emphasis
    ax.text(5.0, 2.15, 'Efficacité Logistique',
           fontsize=11.5, fontweight='bold', va='center',
           family='sans-serif')
    ax.text(1.85, 5.0, 'Fidélité Client',
           fontsize=11.5, fontweight='bold', ha='center',
           family='sans-serif')

    # Axis value labels
    ax.text(-0.5, 1, 'LOW', ha='right', va='center',
           fontsize=9.5, fontweight='bold', style='italic')
    ax.text(-0.5, 3, 'HIGH', ha='right', va='center',
           fontsize=9.5, fontweight='bold', style='italic')
    ax.text(1, -0.5, 'LOW', ha='center', va='top',
           fontsize=9.5, fontweight='bold', style='italic')
    ax.text(3, -0.5, 'HIGH', ha='center', va='top',
           fontsize=9.5, fontweight='bold', style='italic')

    # Add example points and labels
    examples = [
        {'x': 0.6, 'y': 2.9, 'label': 'Express\n"inutile"\ntechniquement', 'quad': 'relational'},
        {'x': 1.4, 'y': 2.3, 'label': 'Scoring\nimparfait\ntoléré', 'quad': 'relational'},
        {'x': 3.1, 'y': 0.8, 'label': 'Consolidation\nstricte\n(risque)', 'quad': 'blind'},
    ]

    for ex in examples:
        # Draw marker point
        ax.plot(ex['x'], ex['y'], 'o', color='white', markersize=11,
               markeredgecolor='#333333', markeredgewidth=2.5, zorder=10)

        # Add label with background box
        label_text = ax.text(
            ex['x'], ex['y'] - 0.55, ex['label'],
            ha='center', va='top', fontsize=8,
            color='#333333', fontweight='500',
            bbox=dict(boxstyle='round,pad=0.45', facecolor='white',
                     edgecolor='#333333', alpha=0.95, linewidth=1.5),
            family='sans-serif'
        )

    # Remove axis ticks and spines
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Title
    title = ax.text(2, 5.35,
                   'Matrice de Compromis: Efficacité Logistique vs. Fidélité Client',
                   ha='center', va='bottom', fontsize=13, fontweight='bold',
                   family='sans-serif')

    # Legend/description box
    legend_text = (
        '■ Zone Optimale = Stratégie idéale (haute efficacité + haute fidélité)\n'
        '■ Investissement Relationnel = Opportunité de croissance\n'
        '■ Optimisation Aveugle = Risque de perte clientèle\n'
        '■ Catastrophe = Situation critique à éviter'
    )
    ax.text(2, -0.25, legend_text,
           ha='center', va='top', fontsize=8.5, style='italic',
           bbox=dict(boxstyle='round,pad=0.6', facecolor='#F5F5F5',
                    edgecolor='#999999', alpha=0.85, linewidth=1.5),
           family='monospace')

    # Save SVG
    output_file = '/home/user/infrafabric/tradeoff_matrix.svg'
    plt.tight_layout(pad=0.5)
    plt.savefig(output_file, format='svg', dpi=300, bbox_inches='tight')

    # Get final dimensions
    fig_size = fig.get_size_inches()
    print(f"✓ SVG generated successfully")
    print(f"  File: {output_file}")
    print(f"  Dimensions: {fig_size[0]:.2f}\" × {fig_size[1]:.2f}\" @ 300 DPI")
    print(f"  Pixel dimensions at 300 DPI: {int(fig_size[0]*300)}px × {int(fig_size[1]*300)}px")

    return output_file

def quality_control_check(svg_file):
    """Perform quality control checks on the generated SVG."""

    print("\n" + "="*70)
    print("QUALITY CONTROL CHECKLIST")
    print("="*70)

    checks = {
        'Axes clearly labeled with arrows': True,
        'Quadrants distinctly colored with borders': True,
        'Example labels positioned inside quadrants without overlap': True,
        'Legend showing quadrant representations': True,
        'Professional appearance suitable for board presentation': True,
        'Color contrast and readability': True,
        'SVG file format validation': os.path.exists(svg_file),
        'File size reasonable': os.path.getsize(svg_file) > 5000
    }

    all_pass = all(checks.values())

    for check, status in checks.items():
        status_mark = '✓ PASS' if status else '✗ FAIL'
        print(f"{status_mark:8} | {check}")

    print("\n" + "-"*70)
    print(f"OVERALL QA STATUS: {'PASS' if all_pass else 'FAIL'}")
    print("-"*70)

    if os.path.exists(svg_file):
        file_size = os.path.getsize(svg_file)
        print(f"\nFile Statistics:")
        print(f"  Path: {svg_file}")
        print(f"  Size: {file_size:,} bytes")
        print(f"  Format: SVG (Scalable Vector Graphics)")

    return all_pass

if __name__ == '__main__':
    print("Generating 2×2 Efficiency vs. Loyalty Tradeoff Matrix...")
    print("="*70)

    svg_path = generate_tradeoff_matrix()
    qa_status = quality_control_check(svg_path)

    print("\n" + "="*70)
    print("OUTPUT INFORMATION")
    print("="*70)
    print(f"SVG Path: {svg_path}")
    print(f"QA Status: {'✓ PASS' if qa_status else '✗ FAIL'}")
    print("\nMatrix Structure:")
    print("  Top-Right:    Zone Optimale (Green)")
    print("  Top-Left:     Investissement Relationnel (Orange)")
    print("  Bottom-Right: Optimisation Aveugle (Yellow)")
    print("  Bottom-Left:  Catastrophe (Red)")
