"""freshtechupdates v2 logo: italic 3D FT (cyan F, cream T, lime slash) as inline SVG."""

F = "M368,355 L913,355 L833,462 L451,462 L386,630 L638,630 L563,732 L351,732 L296,903 L166,903 C210,760 290,520 368,355 Z"
T = "M472,496 L1041,496 L975,597 L812,597 L717,905 L590,905 L682,597 L431,597 Z"
L = "M955,355 L1057,355 L976,462 L873,462 Z"
VIEWBOX = "150 340 935 595"   # tight crop of the mark (incl. extrusion)


def _stack(d, fill, depth):
    return "".join(f'<path d="{d}" fill="{fill}" transform="translate({k*2} {k*2})"/>' for k in range(depth, 0, -1))


def logo_inner(uid="ftl", ids=False, depth=12):
    """SVG fragment in logo coordinates. ids=True gives <g id=uid+F/T/L> groups for animation."""
    i = (lambda s: f' id="{uid}{s}"') if ids else (lambda s: "")
    return (f'<defs><linearGradient id="{uid}c" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8AF0FF"/>'
            f'<stop offset=".45" stop-color="#22D3EE"/><stop offset="1" stop-color="#0FA3C2"/></linearGradient>'
            f'<linearGradient id="{uid}w" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF"/>'
            f'<stop offset=".5" stop-color="#F3EBDD"/><stop offset="1" stop-color="#D8CDBB"/></linearGradient>'
            f'<linearGradient id="{uid}l" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#E4FF9E"/>'
            f'<stop offset="1" stop-color="#A3E635"/></linearGradient></defs>'
            f'<g{i("F")}>{_stack(F, "#0B6C80", depth)}<path d="{F}" fill="url(#{uid}c)"/></g>'
            f'<g{i("T")}>{_stack(T, "#9C9384", depth)}<path d="{T}" fill="url(#{uid}w)"/></g>'
            f'<g{i("L")}>{_stack(L, "#5E8A16", depth)}<path d="{L}" fill="url(#{uid}l)"/></g>')


def logo_svg(width, uid="ftl", ids=False, depth=12, style=""):
    """Standalone <svg> of the mark, `width` px wide (height follows the aspect ratio)."""
    h = round(width * 595 / 935)
    st = f' style="{style}"' if style else ""
    return (f'<svg width="{width}" height="{h}" viewBox="{VIEWBOX}" aria-hidden="true"{st}>'
            f'{logo_inner(uid, ids, depth)}</svg>')
