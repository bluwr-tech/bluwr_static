# Bluwr Static
The easiest way to build static websites

A lightweight Python library for building static websites from reusable HTML **components**, **sections**, and **pages**. You write ordinary HTML templates, compose them with a simple `{{ }}` syntax, and generate ready-to-deploy HTML files.

## Comparison
| Feature | Bluwr Static | Jekyll / Hugo | React / Next.js |
|---|---|---|---|
| Build time | Lightning Fast | OK-Long | OK-Long |
| Authoring format | HTML and YAML-like inserts | Markdown, templates, front matter | JSX/TSX |
| Component reuse | Built in | Template includes/partials | Components |
| Section composition | Built in | Includes/partials | Components |
| Output | Static HTML files | Static HTML and assets | Often JavaScript-driven pages |
| Build complexity | Low | Low to medium | Medium to high |
| Runtime requirements | Python at build time | Generator runtime | Node.js ecosystem |
| Best suited for | Small custom static sites | Content-heavy sites and blogs | Interactive applications |

## Features

Bluwr Static supports:
- Components
- Sections
- ⁠Nested sections
- ⁠Pages
- ⁠Layouts
- ⁠Pseudo-scoped CSS and JS

And:
- It's about 200 lines of python
- Has no boiler plate
- No setup with questions to answer
- No tons of JS dependencies, just pyyaml
- Builds the result really fast

## When to use it

This library is a good fit for:

- Landing pages and marketing sites.
- Portfolios and small business websites.
- Documentation prototypes.
- Design systems and HTML component libraries.
- Projects where you want static HTML without adopting a large framework.
- Teams that prefer HTML templates over JSX, Markdown, or a full CMS.

## Installation

Install the package with pip:

```bash
git clone git@github.com:bluwr-tech/bluwr_static.git
cd bluwr_static
```

Or, if you are developing locally from the repository:

```bash
pip install -e .
```

## Quick start example

Any folder architecture will work, you can have several folders for components, sections and pages, but let's try with the simplest example.

Create this project structure:

```text
my-site/
├── build.py
└── template/
    ├── components/
    │   ├── button.html
    │   └── card.html
    ├── sections/
    │   ├── header.html
    │   └── hero.html
    └── pages/
        └── index.html
```

Create `build.py`:

```python
from bluwr_static import Builder

builder = Builder()

builder.load_components("./template/components")
builder.load_sections("./template/sections")
builder.load_pages("./template/pages")

builder.build("./dist")
```

Run it:

```bash
python build.py
```

The builder writes each page as an HTML file in the output folder:

```text
dist/
└── index.html
```

You can also use the default output directory, which is the current working directory:

```python
builder.build()
```

## Components

Components are the smallest reusable pieces of HTML: buttons, cards, links, badges, form fields, and similar elements.

A component is an HTML file containing `{{ variable }}` placeholders.

### Create a component

`template/components/button.html`

```html
<a class="btn btn--{{ variant }}" href="{{ url }}">
  {{ label }}
</a>
```

`template/components/card.html`

```html
<article class="card">
  <h3 class="card__title">{{ title }}</h3>
  <p class="card__text">{{ description }}</p>
  <a class="card__link" href="{{ url }}">Learn more</a>
</article>
```

### Use a component

Use a component inside a section or page with this syntax:

```html
{{ component_name: {variable: value, another_variable: value} }}
```

Example:

```html
{{ button: {variant: primary, url: /contact, label: Contact us} }}
```

The builder parses the YAML-like content between `{{ }}`. The first key is the component name, and the remaining mapping is passed to the component as its variables.

For the `button.html` component above, this:

```html
{{ button: {variant: primary, url: /contact, label: Contact us} }}
```

renders as:

```html
<a class="btn btn--primary" href="/contact">
  Contact us
</a>
```

### Multiple components

`template/pages/index.html`

```html
<div class="cards">
  {{ card:
    title: Components
    description: Build reusable pieces of HTML.
    url: /docs/components
  }}

  {{ card:
    title: Sections
    description: Combine components into larger page areas.
    url: /docs/sections
  }}
</div>
```

### Variables

Component variables are found with the pattern:

```text
{{ variable_name }}
```

Whitespace around the variable name is ignored:

```html
{{title}}
{{ title }}
{{  title  }}
```

All three are treated as the `title` variable.

### Default values

If a variable is not supplied, it is replaced with the component’s default value. By default, that value is an empty string.

For example, with this component:

```html
<p>{{ optional_note }}</p>
```

This usage:

```html
{{ note: {} }}
```

renders as:

```html
<p></p>
```

### Unknown variables

If you pass a variable that does not exist in the component, the library raises:

```python
ComponentVariableNotFound
```

Example:

```html
{{ button: {variant: primary, url: /, label: Home, color: blue} }}
```

If `button.html` does not contain `{{ color }}`, this raises an error.

## Sections

Sections are reusable page regions: headers, footers, navigation bars, heroes, sidebars, feature grids, and similar blocks.

A section can contain components and can also include other sections.

### Create a section

`template/sections/header.html`

```html
<header class="site-header">
  <a class="site-header__logo" href="/">My Site</a>

  {{ button: {variant: primary, url: /contact, label: Contact} }}
</header>
```

`template/sections/hero.html`

```html
<section class="hero">
  {{ card:
    title: Build reusable pages
    description: Compose components into sections and sections into pages.
    url: /docs
  }}
</section>
```

### Use a section

Reference a section by name:

```html
{{ header }}
{{ hero }}
```

The builder first checks whether the name exists in the loaded sections. If it does, it renders that section. Otherwise, it looks for a component with the same name.

```python
if sections and (match["component"] in sections.files):
    section = sections[match["component"]]
    to_insert = section.build(components, sections)
else:
    component = components[match["component"]]
    to_insert = component.build(match["values"])
```

This means that a section and a component should not share the same name if you need predictable resolution.

### Section with arguments

You can provide arguments in the same YAML-like style:

```html
{{ hero: {title: Welcome} }}
```

The section is rendered and inserted into the page. The arguments are associated with the section insert, but the current rendering flow calls the section without forwarding those values to its internal component inserts.

## Pages

Pages are the final templates. Every page file becomes one output HTML file, named after the source file.

| Source file | Generated file |
|---|---|
| `template/pages/index.html` | `index.html` |
| `template/pages/about.html` | `about.html` |
| `template/pages/pricing.html` | `pricing.html` |

### Create a page

`template/pages/index.html`

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>My static site</title>
  <link rel="stylesheet" href="/assets/site.css">
</head>
<body>
  {{ header }}

  <main>
    {{ hero }}

    <div class="features">
      {{ card:
        title: Components
        description: Reuse small pieces of HTML across the site.
        url: /docs/components
      }}

      {{ card:
        title: Sections
        description: Combine components into larger page regions.
        url: /docs/sections
      }}
    </div>
  </main>

  {{ footer }}
</body>
</html>
```

### Build a page

```python
from bluwr_static import Builder

builder = Builder()

builder.load_components("./template/components")
builder.load_sections("./template/sections")
builder.load_pages("./template/pages")

builder.build("./dist")
```

## Pseudo-scoping CSS and JavaScript

The library does not compile, bundle, or namespace CSS and JavaScript. Instead, use a naming convention that keeps each component’s styles and scripts isolated in practice.

This approach is called **pseudo-scoping**: CSS and JavaScript remain global in the browser, but consistent class and data-attribute naming prevents most accidental conflicts.

### Recommended structure

```text
template/
├── components/
│   ├── button.html
│   ├── card.html
│   └── pricing-table.html
├── sections/
│   ├── header.html
│   └── hero.html
└── pages/
    └── index.html

assets/
├── css/
│   ├── site.css
│   ├── button.css
│   ├── card.css
│   └── pricing-table.css
└── js/
    ├── button.js
    ├── card.js
    └── pricing-table.js
```

### Component HTML

`template/components/pricing-table.html`

```html
<div class="pricing-table" data-pricing-table>
  <h2 class="pricing-table__title">{{ title }}</h2>

  <ul class="pricing-table__plans">
    {{ plan }}
  </ul>

  <button
    class="pricing-table__cta"
    type="button"
    data-pricing-table-cta
  >
    {{ cta_label }}
  </button>
</div>
```

### Component CSS

`assets/css/pricing-table.css`

```css
.pricing-table {
  border: 1px solid #ddd;
  border-radius: 12px;
  padding: 24px;
}

.pricing-table__title {
  margin-top: 0;
}

.pricing-table__plans {
  list-style: none;
  padding: 0;
}

.pricing-table__cta {
  background: #0066ff;
  color: white;
  border: 0;
  border-radius: 8px;
  padding: 12px 20px;
}
```

Use a component-specific root class, such as `.pricing-table`, and prefix all related classes with that name:

```text
.pricing-table
.pricing-table__title
.pricing-table__plans
.pricing-table__cta
```

This prevents a generic class such as `.title` or `.button` from accidentally affecting another component.

### Component JavaScript

`assets/js/pricing-table.js`

```js
(() => {
  const init = () => {
    const roots = document.querySelectorAll("[data-pricing-table]");

    roots.forEach((root) => {
      const button = root.querySelector("[data-pricing-table-cta]");

      if (!button) {
        return;
      }

      button.addEventListener("click", () => {
        root.classList.toggle("pricing-table--expanded");
      });
    });
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
```

Use these conventions:

- Wrap component JavaScript in an IIFE so internal variables do not become global.
- Select components using a component-specific `data-*` attribute.
- Avoid relying on `id` attributes, because IDs must be unique in a document.
- Use class names prefixed with the component name.

### Loading assets

Add CSS and JavaScript links in a shared head section:

`template/sections/head.html`

```html
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <title>{{ title }}</title>

  <link rel="stylesheet" href="/assets/css/site.css">
  <link rel="stylesheet" href="/assets/css/button.css">
  <link rel="stylesheet" href="/assets/css/card.css">
  <link rel="stylesheet" href="/assets/css/pricing-table.css">

  <script defer src="/assets/js/button.js"></script>
  <script defer src="/assets/js/card.js"></script>
  <script defer src="/assets/js/pricing-table.js"></script>
</head>
```

Then include it in every page:

```html
<!doctype html>
<html lang="en">
{{ head: {title: My site} }}

<body>
  {{ header }}
  {{ pricing-table: {title: Plans, cta_label: Choose a plan} }}
  {{ footer }}
</body>
</html>
```

## Building the website

### Full example

`build.py`

```python
from bluwr_static import Builder

builder = Builder()

builder.load_components("./template/components")
builder.load_sections("./template/sections")
builder.load_pages("./template/pages")

builder.build("./dist")
```

Run:

```bash
python build.py
```

### Chained example

The loader methods return the builder, so you can chain them:

```python
from bluwr_static import Builder

(
    Builder()
    .load_components("./template/components")
    .load_sections("./template/sections")
    .load_pages("./template/pages")
    .build("./dist")
)
```

### Output location

`build()` accepts an output folder:

```python
builder.build("./dist")
```

If you omit the argument, the site is written to the current directory:

```python
builder.build()
```

The builder creates the output directory if it does not already exist.

## API

### `Builder`

```python
from bluwr_static import Builder

builder = Builder()
```

| Method | Description |
|---|---|
| `load_components(folder)` | Loads every `*.html` file in `folder` as a component |
| `load_sections(folder)` | Loads every `*.html` file in `folder` as a section |
| `load_pages(folder)` | Loads every `*.html` file in `folder` as a page |
| `build(folder="./")` | Renders all pages and writes them as HTML files |

### `Component`

```python
from bluwr_static import Component

button = Component("./template/components/button.html")

html = button.build({
    "variant": "primary",
    "url": "/contact",
    "label": "Contact us"
})
```

| Member | Description |
|---|---|
| `file` | Path to the component HTML file |
| `template` | Raw component HTML |
| `variables` | Discovered component variables |
| `build(variable_values)` | Returns the rendered HTML |

### `Page`

```python
from bluwr_static import Page

page = Page("./template/pages/index.html")

html = page.build(components, sections)
```

| Member | Description |
|---|---|
| `file` | Path to the page HTML file |
| `template` | Raw page HTML |
| `build(components, sections)` | Renders components and sections into the page |

### Exceptions

| Exception | Meaning |
|---|---|
| `ComponentVariableNotFound` | A component received a variable it does not define |
| `ElementFileNotFound` | A component or section name could not be found |

## Advantages

### Simple authoring model

You only need to learn two patterns:

```html
{{ variable }}
```

```html
{{ component_or_section: {key: value} }}
```

There is no complex template language, no required front matter, and no framework-specific component format.

### HTML-first workflow

Templates are ordinary HTML files. Designers can edit markup directly, while developers can automate rendering through Python.

### Reusable interfaces

Components eliminate repeated markup for buttons, cards, badges, and other UI elements. Sections extend reuse to headers, heroes, navigation, footers, and larger page regions.

### Static output

The builder produces plain HTML files. Static pages are prebuilt rather than rendered on every request, which makes them straightforward to deploy and serve from static hosting or a CDN. 

### Small dependency surface

The library relies on Python’s standard library. You do not need a Node.js toolchain, a frontend framework, or a database to generate the site.

### Easy to understand

The rendering process is explicit: components receive variables, sections render their own inserts, and pages combine both into final HTML files.
