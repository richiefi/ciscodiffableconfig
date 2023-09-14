"""Order-insensitive but order-preserving diff for Cisco-style configs."""


class CiscoDiffableConfigClause:
    def __init__(self, line: str | None = None):
        self.line = line
        self.indent = len(line) - len(line.lstrip()) if line else -1
        self.children: list["CiscoDiffableConfigClause"] = []

    def __hash__(self):
        return hash(self.line)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def config_lines(self, with_prefix: str = "", with_children: bool = True) -> str:
        output = f"{with_prefix}{self.line}\n" if self.line else ""
        if with_children:
            for child in self.children:
                output += child.config_lines(
                    with_prefix=with_prefix, with_children=with_children
                )
        return output


class CiscoDiffableConfig:
    root: CiscoDiffableConfigClause

    def __init__(self, config: str):
        self.root = self._parse_config(config)

    def _parse_config(self, config: str) -> CiscoDiffableConfigClause:
        root = CiscoDiffableConfigClause()
        previous_clause = root
        ancestors = []
        for line in config.splitlines():
            line = line.rstrip()
            if not line or line.lstrip().startswith("!"):
                continue
            clause = CiscoDiffableConfigClause(line)
            if clause.indent > previous_clause.indent:
                ancestors.append(previous_clause)
            elif clause.indent < previous_clause.indent:
                while clause.indent <= ancestors[-1].indent:
                    del ancestors[-1]
            ancestors[-1].children.append(clause)
            previous_clause = clause
        return root

    def diff(self, new: "CiscoDiffableConfig") -> str:
        """Output the new config with diff markers indicating changed lines."""

        def _diff(
            old_clause: CiscoDiffableConfigClause,
            new_clause: CiscoDiffableConfigClause,
        ) -> str:
            printed = set()
            output = ""
            old_iter = iter(old_clause.children)
            new_iter = iter(new_clause.children)
            old_child = next(old_iter, None)
            new_child = next(new_iter, None)
            while old_child or new_child:
                while old_child in printed:
                    old_child = next(old_iter, None)
                while new_child in printed:
                    new_child = next(new_iter, None)
                while old_child and old_child not in new_clause.children:
                    output += old_child.config_lines(with_prefix="-")
                    printed.add(old_child)
                    old_child = next(old_iter, None)
                if (
                    new_child
                    and new_child in old_clause.children
                    and new_child not in printed
                ):
                    output += new_child.config_lines(
                        with_prefix=" ", with_children=False
                    )
                    matching_old_child = old_clause.children[
                        old_clause.children.index(new_child)
                    ]
                    output += _diff(matching_old_child, new_child)
                    printed.add(new_child)
                if (
                    new_child
                    and new_child not in old_clause.children
                    and new_child not in printed
                ):
                    output += new_child.config_lines(with_prefix="+")
                    printed.add(new_child)
            return output

        return _diff(self.root, new.root)

    def concise_diff(self, new: "CiscoDiffableConfig") -> str:
        """Output only the changed lines and their ancestors."""
        full_diff = self.diff(new)
        output_lines = []
        stack: list[tuple[str, int]] = []
        previous_indent = 0
        previous_context_line = None
        for line in full_diff.splitlines():
            indent = len(line[1:]) - len(line[1:].lstrip())
            if indent > previous_indent and previous_context_line:
                stack.append((previous_context_line, previous_indent))
            if indent < previous_indent:
                while len(stack) > 0 and indent <= stack[-1][1]:
                    stack.pop()
            previous_indent = indent
            if line.startswith("-") or line.startswith("+"):
                while len(stack) > 0:
                    output_lines.append(stack.pop(0)[0])
                output_lines.append(line)
                previous_context_line = None
            else:
                previous_context_line = line
        return "\n".join(output_lines)
