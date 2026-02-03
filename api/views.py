import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import UploadHistory

class DataSummaryAPI(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file"}, status=400)

        try:
            df = pd.read_csv(file)
            
            # SAFE CALCULATION: Checks if column exists before calculating
            avg_pressure = df['Pressure'].mean() if 'Pressure' in df.columns else 0.0
            avg_temp = df['Temperature'].mean() if 'Temperature' in df.columns else 0.0
            avg_flowrate = df['Flowrate'].mean() if 'Flowrate' in df.columns else 0.0
            total_count = len(df)

            type_dist = df['Type'].value_counts().to_dict() if 'Type' in df.columns else {}

            # Save to Database
            UploadHistory.objects.create(
                filename=file.name,
                total_count=total_count,
                avg_pressure=avg_pressure,
                avg_temp=avg_temp,
                avg_flowrate=avg_flowrate
            )

            # Fetch History
            recent = UploadHistory.objects.all().order_by('-upload_date')[:5]
            history_data = [{
                "filename": h.filename,
                "upload_date": h.upload_date.isoformat(),
                "avg_pressure": round(h.avg_pressure, 2),
                "avg_flowrate": round(h.avg_flowrate, 2),
                "avg_temp": round(h.avg_temp, 2)
            } for h in recent]

            return Response({
                "total_count": total_count,
                "avg_pressure": round(avg_pressure, 2),
                "avg_temp": round(avg_temp, 2),
                "avg_flowrate": round(avg_flowrate, 2),
                "type_distribution": type_dist,
                "history": history_data
            })

        except Exception as e:
            print(f"CRITICAL ERROR: {str(e)}") # This will show in your terminal
            return Response({"error": str(e)}, status=500)