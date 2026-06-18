"""Allow graphviz-formatted graphs to be included inline in documentation."""

from __future__ import annotations

import re
import subprocess
import urllib.parse
import xml.etree.ElementTree as ET
from hashlib import md5
from os import path
from typing import TYPE_CHECKING, Any, ClassVar

from docutils import nodes
from docutils.parsers.rst import directives

import sphinx
from sphinx.errors import SphinxError
from sphinx.locale import _, __
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective
from sphinx.util.fileutil import ensuredir
from sphinx.util.i18n import search_image_for_language
from sphinx.util.nodes import set_source_info

if TYPE_CHECKING:
    from docutils.nodes import Node

    from sphinx.application import Sphinx
    from sphinx.config import Config
    from sphinx.environment import BuildEnvironment
    from sphinx.util.typing import ExtensionMetadata, OptionSpec

logger = logging.getLogger(__name__)

# Online rendering base URL used when graphviz_allow_web=True.
# QuickChart.io provides a free, public Graphviz rendering API.
_ONLINE_RENDER_URL = "https://quickchart.io/graphviz?graph={code}"


class GraphvizError(SphinxError):
    category = "Graphviz error"


class GraphvizNotFoundError(GraphvizError):
    """Raised specifically when the 'dot' executable cannot be found on the system.

    Distinguishing this from a generic :class:`GraphvizError` allows callers to
    provide friendlier, actionable feedback rather than showing raw DOT source.
    """

    category = "Graphviz not found"


class graphviz(nodes.General, nodes.Inline, nodes.Element):
    pass


class Graphviz(SphinxDirective):
    """Directive to insert arbitrary dot markup."""

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = False
    option_spec: ClassVar[OptionSpec] = {
        "alt": directives.unchanged,
        "inline": directives.flag,
        "caption": directives.unchanged,
        "graphviz_dot": directives.unchanged,
        "layout": directives.unchanged,
        "name": directives.unchanged,
        "class": directives.class_option,
    }

    def run(self) -> list[Node]:
        if self.arguments:
            document = self.state.document
            if self.content:
                return [
                    document.reporter.warning(
                        __(
                            "Graphviz directive cannot have both content and "
                            "a filename argument"
                        ),
                        line=self.lineno,
                    )
                ]
            argument = search_image_for_language(self.arguments[0], self.env)
            rel_filename, filename = self.env.relfn2path(argument)
            self.env.note_dependency(rel_filename)
            try:
                with open(filename, encoding="utf-8") as fp:
                    dotcode = fp.read()
            except OSError as err:
                return [
                    document.reporter.warning(
                        __(
                            "External Graphviz file %r not found or reading "
                            "it failed: %s"
                        )
                        % (filename, err),
                        line=self.lineno,
                    )
                ]
        else:
            dotcode = "\n".join(self.content)
            if not dotcode.strip():
                return [
                    self.state_machine.reporter.warning(
                        __('Ignoring "graphviz" directive without content.'),
                        line=self.lineno,
                    )
                ]

        node = graphviz()
        node["code"] = dotcode
        node["options"] = {"docname": self.env.docname}

        if "graphviz_dot" in self.options:
            node["options"]["graphviz_dot"] = self.options["graphviz_dot"]
        if "layout" in self.options:
            node["options"]["layout"] = self.options["layout"]
        if "alt" in self.options:
            node["alt"] = self.options["alt"]
        if "inline" in self.options:
            node["inline"] = True
        if "caption" in self.options:
            node["caption"] = self.options["caption"]
        if "class" in self.options:
            node["classes"] = self.options["class"]

        set_source_info(self, node)
        return [node]


class GraphvizSimple(SphinxDirective):
    """Directive for generating a graphviz graph from a simple dot language fragment."""

    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec: ClassVar[OptionSpec] = {
        "alt": directives.unchanged,
        "inline": directives.flag,
        "caption": directives.unchanged,
        "graphviz_dot": directives.unchanged,
        "layout": directives.unchanged,
        "name": directives.unchanged,
        "class": directives.class_option,
    }

    def run(self) -> list[Node]:
        node = graphviz()
        node["code"] = "%s %s {\n%s\n}\n" % (
            self.name,
            self.arguments[0],
            "\n".join(self.content),
        )
        node["options"] = {"docname": self.env.docname}

        if "graphviz_dot" in self.options:
            node["options"]["graphviz_dot"] = self.options["graphviz_dot"]
        if "layout" in self.options:
            node["options"]["layout"] = self.options["layout"]
        if "alt" in self.options:
            node["alt"] = self.options["alt"]
        if "inline" in self.options:
            node["inline"] = True
        if "caption" in self.options:
            node["caption"] = self.options["caption"]
        if "class" in self.options:
            node["classes"] = self.options["class"]

        set_source_info(self, node)
        return [node]


def fix_svg_relative_path(content: str, refuri: str) -> str:
    """Replace relative links inside an SVG with absolute paths using *refuri* as base."""

    def _fix(match: re.Match) -> str:
        uri = match.group(1)
        if "://" not in uri:
            uri = refuri + uri
        return f'xlink:href="{uri}"'

    return re.sub(r'xlink:href="([^"]*)"', _fix, content)


def generate_name(
    self: Any,
    node: graphviz,
    fileformat: str,
) -> tuple[str, str]:
    """Return (relative-output-path, absolute-output-path) for a rendered image."""
    key = md5(node["code"].encode(), usedforsecurity=False).hexdigest()
    fname = "graphviz-%s.%s" % (key, fileformat)
    relfn = path.join(self.builder.imagedir, fname)
    outfn = path.join(self.builder.outdir, self.builder.imagedir, fname)
    return relfn, outfn


def _save_dot_source(code: str, outfn: str) -> str:
    """Persist the raw DOT *code* next to *outfn* and return the .dot file path.

    The intermediate ``.dot`` file is always written so that readers can
    inspect or manually render it when the local ``dot`` binary is absent.
    """
    dot_outfn = path.splitext(outfn)[0] + ".dot"
    ensuredir(path.dirname(dot_outfn))
    with open(dot_outfn, "w", encoding="utf-8") as f:
        f.write(code)
    return dot_outfn


def render_dot(
    self: Any,
    code: str,
    options: dict[str, Any],
    fileformat: str,
    prefix: str = "graphviz",
    filename: str | None = None,
) -> tuple[str | None, str | None]:
    """Render *code* via the local ``dot`` binary and return ``(relfn, outfn)``.

    Raises
    ------
    GraphvizNotFoundError
        When the ``dot`` executable is not installed / not on ``PATH``.
    GraphvizError
        For any other rendering failure (bad dot syntax, non-zero exit, etc.).
    """
    graphviz_dot = options.get(
        "graphviz_dot", self.builder.config.graphviz_dot
    )

    relfn, outfn = generate_name(self, {"code": code}, fileformat)  # type: ignore[arg-type]

    if path.isfile(outfn):
        return relfn, outfn

    ensuredir(path.dirname(outfn))

    # Always persist the intermediate .dot source so it can be linked.
    _save_dot_source(code, outfn)

    dot_args = [graphviz_dot]
    if self.builder.config.graphviz_dot_args:
        dot_args.extend(self.builder.config.graphviz_dot_args)

    layout = options.get("layout")
    if layout:
        dot_args.extend(["-K", layout])

    dot_args.extend(["-T", fileformat, "-o", outfn])

    try:
        ret = subprocess.run(
            dot_args,
            input=code.encode(),
            capture_output=True,
            check=False,
        )
    except FileNotFoundError as exc:
        # 'dot' binary is absent — raise a typed error so callers can
        # distinguish this case and show a friendly placeholder instead of
        # dumping raw DOT source onto the page.
        raise GraphvizNotFoundError(
            __(
                "The 'dot' drawing application (Graphviz) was not found on "
                "this system. Install Graphviz from https://www.graphviz.org/ "
                "to render diagrams locally. (original error: %s)"
            )
            % exc
        ) from exc
    except OSError as exc:
        raise GraphvizError(
            __(
                "dot command %r cannot be run (Graphviz must be installed); "
                "see https://www.graphviz.org/ — error: %s"
            )
            % (graphviz_dot, exc)
        ) from exc

    if ret.returncode != 0:
        raise GraphvizError(
            __("dot exited with error:\n[stderr]\n%r\n[stdout]\n%r")
            % (ret.stderr, ret.stdout)
        )

    return relfn, outfn


# ---------------------------------------------------------------------------
# Helper: graceful HTML error placeholder
# ---------------------------------------------------------------------------

def _dot_source_relfn(relfn: str) -> str:
    """Derive the relative path of the intermediate .dot file from *relfn*."""
    return path.splitext(relfn)[0] + ".dot"


def _build_missing_dot_placeholder(
    code: str,
    dot_relfn: str | None,
    allow_web: bool,
) -> str:
    """Return an HTML snippet to show when the local ``dot`` binary is absent.

    Parameters
    ----------
    code:
        The raw DOT source so we can optionally build an online render URL.
    dot_relfn:
        Relative path to the intermediate ``.dot`` file, or ``None`` if
        unavailable.
    allow_web:
        If ``True``, embed an ``<img>`` rendered by the QuickChart.io API
        instead of the text placeholder.
    """
    if allow_web:
        encoded = urllib.parse.quote(code, safe="")
        img_url = _ONLINE_RENDER_URL.format(code=encoded)
        parts = [
            '<div class="graphviz-fallback graphviz-web-fallback">',
            f'  <img src="{img_url}" alt="Graphviz diagram (rendered online)" '
            f'       style="max-width:100%;" />',
        ]
        if dot_relfn:
            parts.append(
                f'  <p class="graphviz-source-link">'
                f'    <a href="{dot_relfn}">[View DOT source]</a>'
                f"  </p>"
            )
        parts.append("</div>")
        return "\n".join(parts)

    # Plain error placeholder — no online call.
    lines = [
        '<div class="graphviz-error" style="'
        "border:1px solid #e05252;background:#fff5f5;padding:1em;"
        'border-radius:4px;margin:1em 0;">',
        "  <strong>&#9888; Graphviz diagram could not be rendered</strong>",
        "  <p>The <code>dot</code> drawing application is missing from this "
        "  system. Install <a href='https://www.graphviz.org/'>Graphviz</a> "
        "  to render diagrams locally.</p>",
    ]
    if dot_relfn:
        lines.append(
            f"  <p><a href='{dot_relfn}'>View the intermediate DOT source file</a></p>"
        )
    lines.append("</div>")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# HTML visitor
# ---------------------------------------------------------------------------

def render_dot_html(
    self: Any,
    node: graphviz,
    code: str,
    options: dict[str, Any],
    prefix: str = "graphviz",
    imgcls: str | None = None,
    alt: str | None = None,
    filename: str | None = None,
) -> None:
    """Render *node* as an HTML image and write the tag to the output body."""
    fileformat = self.builder.config.graphviz_output_format
    if fileformat not in ("png", "svg"):
        raise GraphvizError(
            __(
                "graphviz_output_format must be one of 'png', 'svg', but is %r"
            )
            % fileformat
        )

    try:
        relfn, outfn = render_dot(self, code, options, fileformat, prefix, filename)
    except GraphvizNotFoundError:
        # 'dot' is missing — emit a graceful placeholder instead of raw text.
        allow_web: bool = self.builder.config.graphviz_allow_web

        # Try to determine the .dot source link.  We need to compute the
        # output filename without actually calling dot, so we replicate the
        # path generation logic.
        try:
            _relfn, _outfn = generate_name(self, node, fileformat)
            _save_dot_source(code, _outfn)
            dot_relfn = _dot_source_relfn(_relfn)
        except Exception:
            dot_relfn = None

        placeholder = _build_missing_dot_placeholder(code, dot_relfn, allow_web)
        self.body.append(placeholder)
        raise nodes.SkipNode from None

    except GraphvizError as exc:
        logger.warning(
            __("dot code %r: %s"),
            code,
            exc,
            location=node,
            type="graphviz",
            subtype="graphviz",
        )
        raise nodes.SkipNode from None

    self.body.append(self.starttag(node, "div", CLASS="graphviz"))
    if fileformat == "svg":
        try:
            with open(outfn, encoding="utf-8") as f:
                svgdata = f.read()
            # Strip the XML declaration so the SVG embeds cleanly.
            svgdata = re.sub(r"<\?xml[^>]*\?>", "", svgdata)
            self.body.append(svgdata)
        except OSError:
            self.body.append(
                '<p class="graphviz-error">Could not read rendered SVG.</p>'
            )
    else:
        imgnode = nodes.image()
        imgnode["uri"] = relfn
        if alt:
            imgnode["alt"] = alt
        if imgcls:
            imgnode["classes"] = [imgcls]
        self.visit_image(imgnode)
        self.depart_image(imgnode)

    self.body.append("</div>\n")
    raise nodes.SkipNode


def html_visit_graphviz(self: Any, node: graphviz) -> None:
    render_dot_html(
        self,
        node,
        node["code"],
        node["options"],
        imgcls="graphviz",
        alt=node.get("alt"),
    )


# ---------------------------------------------------------------------------
# LaTeX visitor
# ---------------------------------------------------------------------------

def render_dot_latex(
    self: Any,
    node: graphviz,
    code: str,
    options: dict[str, Any],
    prefix: str = "graphviz",
    filename: str | None = None,
) -> None:
    try:
        relfn, outfn = render_dot(self, code, options, "pdf", prefix, filename)
    except GraphvizNotFoundError:
        logger.warning(
            __(
                "Graphviz 'dot' application not found; skipping diagram in "
                "LaTeX output. Install Graphviz to render diagrams."
            ),
            location=node,
            type="graphviz",
            subtype="graphviz",
        )
        raise nodes.SkipNode from None
    except GraphvizError as exc:
        logger.warning(
            __("dot code %r: %s"),
            code,
            exc,
            location=node,
            type="graphviz",
            subtype="graphviz",
        )
        raise nodes.SkipNode from None

    is_inline = node.get("inline", False)
    if is_inline:
        para_separator = ""
    else:
        para_separator = "\n"

    if relfn.endswith(".pdf"):
        self.body.append(
            "%s\\includegraphics{%s}%s" % (para_separator, outfn, para_separator)
        )
    raise nodes.SkipNode


def latex_visit_graphviz(self: Any, node: graphviz) -> None:
    render_dot_latex(self, node, node["code"], node["options"])


# ---------------------------------------------------------------------------
# Texinfo visitor
# ---------------------------------------------------------------------------

def render_dot_texinfo(
    self: Any,
    node: graphviz,
    code: str,
    options: dict[str, Any],
    prefix: str = "graphviz",
) -> None:
    try:
        relfn, outfn = render_dot(self, code, options, "png", prefix)
    except GraphvizNotFoundError:
        logger.warning(
            __(
                "Graphviz 'dot' application not found; skipping diagram in "
                "Texinfo output. Install Graphviz to render diagrams."
            ),
            location=node,
            type="graphviz",
            subtype="graphviz",
        )
        raise nodes.SkipNode from None
    except GraphvizError as exc:
        logger.warning(
            __("dot code %r: %s"),
            code,
            exc,
            location=node,
            type="graphviz",
            subtype="graphviz",
        )
        raise nodes.SkipNode from None

    self.body.append("@image{%s,,,[graphviz],png}\n" % outfn[:-4])
    raise nodes.SkipNode


def texinfo_visit_graphviz(self: Any, node: graphviz) -> None:
    render_dot_texinfo(self, node, node["code"], node["options"])


# ---------------------------------------------------------------------------
# Generic / text visitors (no-op)
# ---------------------------------------------------------------------------

def man_visit_graphviz(self: Any, node: graphviz) -> None:
    if "alt" in node:
        self.body.append(_("[graph: %s]") % node["alt"])
    else:
        self.body.append(_("[graph]"))
    raise nodes.SkipNode


def text_visit_graphviz(self: Any, node: graphviz) -> None:
    if "alt" in node:
        self.add_text(_("[graph: %s]") % node["alt"])
    else:
        self.add_text(_("[graph]"))
    raise nodes.SkipNode


# ---------------------------------------------------------------------------
# setup()
# ---------------------------------------------------------------------------

def setup(app: Sphinx) -> ExtensionMetadata:
    app.add_node(
        graphviz,
        html=(html_visit_graphviz, None),
        latex=(latex_visit_graphviz, None),
        texinfo=(texinfo_visit_graphviz, None),
        man=(man_visit_graphviz, None),
        text=(text_visit_graphviz, None),
    )

    app.add_directive("graphviz", Graphviz)
    app.add_directive("graph", GraphvizSimple)
    app.add_directive("digraph", GraphvizSimple)

    # --- existing configuration values ---
    app.add_config_value("graphviz_dot", "dot", "env")
    app.add_config_value("graphviz_dot_args", [], "env")
    app.add_config_value("graphviz_output_format", "png", "env")

    # --- CAP-11: new configuration value ---
    app.add_config_value(
        "graphviz_allow_web",
        default=False,
        rebuild="env",
        description=(
            "When True and the local 'dot' application is absent, the extension "
            "falls back to rendering diagrams via an online Graphviz web service "
            "(QuickChart.io). Requires an active internet connection during the "
            "documentation build. Defaults to False."
        ),
    )

    return {
        "version": sphinx.__version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
