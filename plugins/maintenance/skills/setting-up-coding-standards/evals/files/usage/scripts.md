# Script standards

<a id="script-001"></a>
## SCRIPT-001: Imports have no side effects

Scripts under scripts/ must defer execution to a main function guarded by
`if __name__ == "__main__"`. This requirement does not govern library modules.
