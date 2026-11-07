# Pruebas del modelo vigente

Consultar [modelo actualizado](../docs/modelo-actualizado.md) para migración, correspondencias y límites.

```sh
python -m unittest discover -s tests -p "test_*.py" -v
node --test tests/auth-client.test.cjs tests/registration-validation.test.mjs
```

Las pruebas usan bases aisladas. Cubren registro, acceso, revocación, permisos, perfil real, esquema sin carné, auditoría sin hashes, integridad de relaciones, reglas de experiencias, migración, rollback y repetición de Alembic.
