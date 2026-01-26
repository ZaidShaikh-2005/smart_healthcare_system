from django.core.management.base import BaseCommand
import pandas as pd
from app.models import Symptom
from pathlib import Path

class Command(BaseCommand):
    help = "Import real symptoms from dataset.csv"

    def handle(self, *args, **kwargs):

        file_path = Path("archive/dataset.csv")

        df = pd.read_csv(file_path)

        symptom_columns = [c for c in df.columns if c.startswith("Symptom")]

        unique_symptoms = set()

        for col in symptom_columns:
            for val in df[col].dropna():
                unique_symptoms.add(val)

        for symptom in unique_symptoms:
            Symptom.objects.get_or_create(
                name=str(symptom).replace("_", " ").title()
            )

        self.stdout.write(self.style.SUCCESS("✅ REAL symptoms imported"))
