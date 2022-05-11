# PDF Generator

This is a simple script that generates PDF documents based on a yaml specification file.

## YAML objects

Currently, these objects are supported:
- [x] Paragraph (text)
- [x] Table
- [ ] Image

## YAML Syntax

The objects listed above should adhere to the following rules.

### Paragraph

```yaml
paragraph:
  text: "Incubator - UDI (S/N: 123455668)"
  alignment: 'center'
  size: 10
  space_before: 4
  space_after: 20
```

### Table

```yaml
table:
  rows:
    - row:
      - text: "Cel1"
      - text: "Cell2"
    - row:
      - text: "Cell3"
      - text: "Cell4"
```