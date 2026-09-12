# Unknown-field rule

An implementation that does not understand a field must not silently erase, reinterpret, normalize, or claim authority over that field merely because it can parse the surrounding object.

Preferred states:

1. preserve the unknown field opaquely;
2. expose that it is unknown;
3. refuse if transporting it would be unsafe or dishonest.

Dropping unknown state by default is a foundation failure.

Opaque preservation is not understanding. It proves only that state owned elsewhere was carried without mutation inside the tested boundary.
