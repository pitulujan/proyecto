"""schedule type and cron

Revision ID: 71fb218fc4f0
Revises: 75db4c7c2bbf
Create Date: 2019-01-13 21:11:51.694710

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '71fb218fc4f0'
down_revision = '75db4c7c2bbf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('scheduled_events', sa.Column('event_cron', sa.String(length=32), nullable=True))
    op.add_column('scheduled_events', sa.Column('event_type', sa.String(length=8), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('scheduled_events', 'event_type')
    op.drop_column('scheduled_events', 'event_cron')
    # ### end Alembic commands ###
