"""init_db

Revision ID: 555d2a91c348
Revises:
Create Date: 2026-02-20 12:08:01.714079

"""

from collections.abc import Sequence
from typing import Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "555d2a91c348"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    ID = "id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY"
    CRAETED_AT = "created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP"

    # department cycles check function
    op.execute("""
        CREATE OR REPLACE FUNCTION check_department_cycle()
        RETURNS TRIGGER AS $$
        DECLARE
            is_cycle BOOLEAN;
        BEGIN
            if (TG_OP = 'UPDATE' AND NEW.parent_id IS NOT NULL) THEN
                WITH RECURSIVE lineage AS (
                    SELECT id, parent_id FROM department WHERE id = NEW.parent_id
                    UNION ALL
                    SELECT d.id, d.parent_id from department d
                    INNER JOIN lineage l on d.id = l.parent_id
                )
                SELECT EXISTS (SELECT 1 FROM lineage WHERE id = NEW.id) INTO is_cycle;

                IF is_cycle THEN
                    RAISE EXCEPTION 'Circular referene detected: Department % cannot be a child of its own descendant.',
                    NEW.id;
                END IF;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # NOTE: there is no constraint that names of departments without parents
    # must be unique, but it is a logical thing to do.
    # I assume that is supposed to be and was missed by the alalytics team.
    # If not, change unique constraint.
    op.execute(f"""
        CREATE TABLE department (
            {ID},
            name VARCHAR(200) NOT NULL,
            parent_id int,
            {CRAETED_AT},

            CONSTRAINT fk_department_parent_id
                FOREIGN KEY(parent_id)
                REFERENCES department(id)
                ON DELETE CASCADE,

            CONSTRAINT depratment_parent_id_unique_name
                UNIQUE NULLS NOT DISTINCT (parent_id, name),

            CONSTRAINT department_parent_id_not_itself
                CHECK (parent_id <> id)
        );

        CREATE TRIGGER trg_prevent_department_cycle
        BEFORE INSERT OR UPDATE OF parent_id on department
        FOR EACH ROW
        EXECUTE FUNCTION check_department_cycle();
    """)

    op.execute(f"""
        CREAETE TABLE employee (
            {ID},
            department_id INT,
            full_name VARCHAR(200) NOT NULL,
            position VARCHAR(200) NOT NULL,
            hired_at TIMESTAMPTZ,
            {CRAETED_AT},

            CONSTRAINT fk_employee_department_id
                FOREIGN KEY(department_id)
                REFERENCES department(id)
                ON_DELETE CASCADE
        );
    """)

    pass


def downgrade() -> None:
    pass
