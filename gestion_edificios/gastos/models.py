from django.db import models
from datetime import date
from django.utils.timezone import now

class Departamento(models.Model):
    numero = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.numero

class GastoComun(models.Model):
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)
    mes = models.IntegerField()
    año = models.IntegerField()
    monto = models.FloatField()
    pagado = models.BooleanField(default=False)
    fecha_pago = models.DateField(null=True, blank=True)

    def estado_pago(self):
        if self.pagado and self.fecha_pago:
            return "Pago dentro del plazo" if date(self.año, self.mes, 1) >= self.fecha_pago else "Pago fuera del plazo"
        return "Pendiente"

    def __str__(self):
        return f"{self.departamento.numero} - {self.mes}/{self.año}"
    
class Solicitud(models.Model):
    departamento = models.ForeignKey('Departamento', on_delete=models.CASCADE, related_name='solicitudes')
    descripcion = models.TextField()
    fecha_solicitud = models.DateTimeField(default=now)
    estado = models.CharField(max_length=20, choices=[('pendiente', 'Pendiente'), ('aprobada', 'Aprobada')], default='pendiente')

    def __str__(self):
        return f"Solicitud {self.id} - Departamento {self.departamento.numero}"
