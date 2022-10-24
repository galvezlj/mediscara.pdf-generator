# PDF Generator

This is a simple script that generates PDF documents based on a yaml specification file.

## YAML objects

Currently, these objects are supported:
- [x] Paragraph (text)
- [x] Table
- [x] Image

All of the object listed support the the alignment attribute.
This can be used to align the element horizontally.
Alignment values can be:
- center
- left
- right

The `Paragraph`, `Image` and `Table` items can define a `space_before` and `space_after` attribute to define a margin vertically.

### Variable placeholders

Some values can be dynamically loaded into the document.
To define a variable placeholder, use the `<variable name>` syntax.

Then, to load the values into the placeholders, use the `pdfgen.yaml.load_variables` method. This returns a dictionary which can be used in place of the original dictionary.

Example:

```yaml
paragraph:
  text: "Incubator - UDI (S/N: <serial_number>)"
  alignment: 'center'
  size: 10
  space_before: 4
  space_after: 20
```

If the `{"serial_number": "123456789"}` dictionary is used in the `load_variables` method the resulting paragraph object would look like this:

```yaml
paragraph:
  text: "Incubator - UDI (S/N: 123456789)"
  alignment: 'center'
  size: 10
  space_before: 4
  space_after: 20
```

## YAML Syntax

### Paragraph

```yaml
paragraph:
  text: "Incubator - UDI (S/N: 123455668)"
  alignment: 'center'
  size: 10
  space_before: 4
  space_after: 20
```

The `size` attribute can be used to set the text size.

### Table

```yaml
table:
  border: false
  header: true
  grid: true
  rows:
    - row:
      - cell:
          text: "Cel1"
      - cell:
          text: "Cell2"
    - row:
      - image:
          resource: 'img/img1.png'
          alignment: center
          width: 50
          height: 50
      - image:
          resource: 'img/img2.png'
          alignment: center
          width: 50
          height: 50
```

The `Table` object must have one `rows` attribute.
This can contain multiple `row` items.
A row can have one or more children. The children can be either `cell` or `image`. The cell element must have a `text` attribute. Optionally the `background_color` attribute can be used to color the background of the cell.

The `border` attribute can be used to define an outer border to the table.
The `header` attribute can be used to separate the first row of the table as a header row.
The `grid` attribute can be used to draw lines between the cells in the table.

## Image

```yaml
image:
  resource: 'img/img1.png'
  alignment: center
  width: 50
  height: 50
```

The `resource` attribute sets the filepath at which the image itself is located.
The `width` and `height` attributes can be used to scale the image.
