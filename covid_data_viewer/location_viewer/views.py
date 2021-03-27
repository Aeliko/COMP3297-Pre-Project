from django import http
from django.forms.forms import Form
from django.forms.models import ModelChoiceField
from django.shortcuts import get_object_or_404, redirect, render
from requests.models import ConnectionError, MissingSchema
from .models import Location
from django.forms import ModelForm
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.


def index(request):
    try:
        default_location_id = Location.objects.get(
            location_name='Hong Kong').pk
        return detail(request, default_location_id)
    except ObjectDoesNotExist:
        return detail(request, 0)


def detail(request, location_id):
    if request.method == 'POST':
        form = SelectLocationForm(request.POST)
        if form.is_valid():
            try:
                new_location = form.cleaned_data['location']
                return redirect(new_location)
            except:
                redirect('index')

    try:
        location = Location.objects.get(pk=location_id)
        context = {
            'location':
            location.location_name,
            'location_id':
            location.id,
            'data':
            getCovidStatistics(location.api_endpoint, location.resource_url,
                               location.current_estimated_population),
            'location_list':
            SelectLocationForm()
        }
    except ObjectDoesNotExist:
        context = {
            'data': {
                'error':
                'Location does not exist in database, please add a new Location.'
            }
        }
    return render(request, 'location_viewer/index.html', context)


class SelectLocationForm(Form):
    location = ModelChoiceField(queryset=Location.objects.all())


class LocationForm(ModelForm):
    class Meta:
        model = Location
        fields = (
            'location_name',
            'api_endpoint',
            'resource_url',
            'current_estimated_population',
        )

    def clean_location_name(self):
        return self.cleaned_data['location_name'].title()


def add(request, location_id=None):
    if request.method == 'POST':
        if location_id is not None:
            try:
                location = Location.objects.get(pk=location_id)
                form = LocationForm(request.POST, instance=location)
            except:
                form = LocationForm(request.POST)
        else:
            form = LocationForm(request.POST)
        if form.is_valid():
            new_location = form.save()
            return redirect(new_location)
    else:
        if location_id is not None:
            try:
                location = Location.objects.get(pk=location_id)
                form = LocationForm(instance=location)
            except:
                form = LocationForm()
        else:
            form = LocationForm()
    return render(request, 'location_viewer/add.html', {
        'form': form,
        'location_id': location_id,
    })


def delete(request, location_id):
    if request.method == 'POST':
        if request.POST.get('Delete', False) == 'Delete':
            Location.objects.get(pk=location_id).delete()
        return redirect('index')
    else:
        location = get_object_or_404(Location, pk=location_id)
        return render(request, 'location_viewer/delete.html',
                      {'location': location})


def getCovidStatistics(api_endpoint, resource_url,
                       current_estimated_population):
    import requests
    import json
    import datetime

    class Response422Exception(Exception):
        pass

    def getCovidData(date) -> dict:
        params = {
            "q":
            json.dumps({
                "resource": resource_url,
                "section": 1,
                "format": "json",
                "filters": [[1, "eq", [date]]]
            })
        }
        results = requests.get(api_endpoint, params=params)
        if results.status_code == 422:
            raise Response422Exception
        return results.json()[0]

    try:
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        dayBeforeYesterday = yesterday - datetime.timedelta(days=1)
        sevenDaysAgo = yesterday - datetime.timedelta(days=7)
        yesterdayData = getCovidData(yesterday.strftime("%d/%m/%Y"))
        dayBeforeYesterdayData = getCovidData(
            dayBeforeYesterday.strftime("%d/%m/%Y"))
        sevenDaysAgoData = getCovidData(sevenDaysAgo.strftime("%d/%m/%Y"))

        dateString = yesterday.strftime('%d/%m/%Y')
        totalConfirmedCases = yesterdayData['Number of confirmed cases']
        totalConfirmedCasesPerMillion = yesterdayData[
            'Number of confirmed cases'] / current_estimated_population * 1000000
        totalFatalities = yesterdayData['Number of death cases']
        totalFatalitiesPerMillion = yesterdayData[
            'Number of death cases'] / current_estimated_population * 1000000
        numNewCases = yesterdayData[
            'Number of confirmed cases'] - dayBeforeYesterdayData[
                'Number of confirmed cases']
        sevenDayAverageNumNewCases = yesterdayData[
            'Number of confirmed cases'] - sevenDaysAgoData[
                'Number of confirmed cases']
        numNewFatalities = yesterdayData[
            'Number of death cases'] - dayBeforeYesterdayData[
                'Number of death cases']
        sevenDayAverageNumNewFatalities = yesterdayData[
            'Number of death cases'] - sevenDaysAgoData['Number of death cases']
        return {
            "date": dateString,
            "totalConfirmedCases": totalConfirmedCases,
            "totalConfirmedCasesPerMillion": totalConfirmedCasesPerMillion,
            "totalFatalities": totalFatalities,
            "totalFatalitiesPerMillion": totalFatalitiesPerMillion,
            "numNewCases": numNewCases,
            "sevenDayAverageNumNewCases": sevenDayAverageNumNewCases,
            "numNewFatalities": numNewFatalities,
            "sevenDayAverageNumNewFatalities": sevenDayAverageNumNewFatalities,
        }
    except (ConnectionError, MissingSchema, json.decoder.JSONDecodeError):
        # first 2 errors are for non-existing websites, the third one is for wrong URLs
        return {'error': 'Wrong API endpoint'}
    except Response422Exception:
        return {'error': 'Wrong resource URL'}
    except Exception as e:
        return {'error': f'{type(e).__name__}, {e.args}'}