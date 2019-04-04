from django.shortcuts import render,redirect,get_object_or_404
from . forms import *
from . models import *
from django.http import HttpResponseRedirect,HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from  organiser_app.serializers import  CandidateSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib import messages
import schedule
import time
import datetime

region_options={

 '0':'AndhraPradesh' ,
 '1':'Bihar' ,
 '2':'karnataka',
 '3':'Tamilnadu' ,
 '4':'Kerela' ,
 '5':'UttarPradesh',
 '6':'WestBengal' ,
 '7':'MadhyaPradesh' ,
 '8':'Haryana' ,
 '9':'Assam'

}


# Create your views here.
@login_required
def party(request):
    party_form = PartyForm()
    context = {'party_form':party_form}
    return render(request, 'organiser_app/party.html',context)



@login_required
def index(request):
    region_form = RegionForm()
    context = {'region_form':region_form}
    return render(request, 'organiser_app/index.html',context)

@login_required
def srchcandidate(request):
    candidate_id=request.POST.get('Candidateid')

    try:
        object = Candidate.objects.get(candidate_id=candidate_id)
        region=region_options[object.candidate_region]
        context = {'object': object,'region':region}
        return render(request, 'organiser_app/candidate_info.html', context=context)
    except:
        message ='Sorry,' + 'Candidate Id "' + str(candidate_id) + '" does not exist.'
        context = {'message': message}
        return render(request, 'organiser_app/candidate_info.html', context=context)

    return render(request,'organiser_app/index.html',context)

@login_required
def candidate_page(request):

    if request.method =="POST":
        candidate_form=Candidateform(request.POST, request.FILES)

        if candidate_form.is_valid():

            #if (datetime.date.today() - (candidate_form.candidate_dob)).days < 365*25:
            #    message = 'Candidate Age is less than"' + str(candidate_form.candidate_dob) + '" years'
            #    context = {'message': message}
            #    return render(request, 'organiser_app/addcandidate.html', context=context)

            #else:
            object=candidate_form.save()
            region=region_options[object.candidate_region]
            context={'object':object,'region':region}
            return render(request,'organiser_app/candidate_info.html',context)

        else:
            print(candidate_form.errors)

    else:
        candidate_form=Candidateform()

    return render(request, 'organiser_app/addcandidate.html', {'candidate_form':candidate_form })

@login_required
def main_page(request):
    return render(request,'organiser_app/index1.html')

@login_required
def election(request):
    election_instance=Election.objects.all()
    context={'election_instance':election_instance}
    return render(request,'organiser_app/election.html',context)

# ------------------------------------Voter Code--------------------------------------------

@login_required
def add_voter(request):

    if request.method == 'POST':

        voter_form = Voterform(data=request.POST)

        if voter_form.is_valid():

                voter_form.save(commit=True)
                message = 'Voter is added successfully!'
                return render(request, 'organiser_app/add_voter.html', {'voter_form': voter_form, 'message': message})

        else:
            print(voter_form.errors)
    else:
        voter_form = Voterform()

    return render(request, 'organiser_app/add_voter.html', {'voter_form':voter_form})

@login_required
def select_region_page(request):

    region_form = RegionForm()

    context = {'region_form':region_form}

    return render(request, 'organiser_app/select_region.html',context)

@login_required
def search_voter(request):

    if request.method == 'POST':
        voterid = request.POST.get('voterid')
        try:
            voter = Voter.objects.get(voter_id=voterid)
            context = {'voter': voter}
            return render(request, 'organiser_app/search_results.html', context=context)
        except:
            message = 'Voter Id "' + str(voterid) + '" does not exist.'
            context = {'message': message}
            return render(request, 'organiser_app/search_results.html', context=context)

    return render(request, 'organiser_app/search_results.html')

@login_required
def voter_region_page(request,pk):
    template_name='organiser_app/voters_list.html'
    voters = Voter.objects.filter(voter_region=pk)
    context = {'voters':voters}
    return render(request,template_name,context)

@login_required
def voter_view(request, pk):
    template_name = 'organiser_app/voter_info.html'
    voter=get_object_or_404(Voter, pk=pk)
    region = region_options[voter.voter_region]
    context = {'voter': voter, 'region': region}
    return render(request, template_name, context=context)

@login_required
def voter_update(request, pk):
    template_name = 'organiser_app/update_voter_form.html'
    voter = get_object_or_404(Voter, pk=pk)
    voter_form = Voterform(request.POST or None, instance=voter)
    if request.method == 'POST':
        if voter_form.is_valid():
            voter_form.save()
            message = 'Voter Id "' + str(voter.voter_id) + '" is updated successfully!'
            return render(request, template_name, {'voter_form': voter_form, 'message': message})
    return render(request, template_name, {'voter_form': voter_form})


def search_voter(request):

    if request.method == 'POST':
        voterid = request.POST.get('voterid')
        try:
            voter = Voter.objects.get(voter_id=voterid)
            context = {'voter': voter}
            return render(request, 'organiser_app/search_results.html', context=context)
        except:
            message = 'Voter Id "' + str(voterid) + '" does not exist.'
            context = {'message': message}
            return render(request, 'organiser_app/search_results.html', context=context)

    return render(request, 'organiser_app/search_results.html')


#-------------------------------------------End Voter Code---------------------------------------------

@login_required
def addelection(request):
    if request.method=="POST":
        addelection_form=Electionform(data=request.POST)

        if addelection_form.is_valid():
            election_instance = addelection_form.save()

            for candidate in election_instance.candidates.all():

                candidate_election_instance = Candidate_election()
                candidate_election_instance.candidate = candidate
                candidate_election_instance.election = election_instance
                candidate_election_instance.save()

            if election_instance.election_type == 'P':
                for i in range(0,10):
                    election_region_instance=Election_region()
                    election_region_instance.region=i
                    election_region_instance.election=election_instance
                    election_region_instance.save()

            if election_instance.election_type=='A':
                election_region_instance=Election_region()
                region=request.POST['statelist']
                election_region_instance.region=region
                election_region_instance.election=election_instance
                election_region_instance.save()

            #region=[]


            election_instance=Election.objects.all()
            #for election in election_instance:
                #region.append(Election_region.objects.get(election=election.election_id))

            #election_region = zip(election_instance, region)

            context={'election_instance':election_instance}
            return render(request,'organiser_app/election.html',context)

        else:
            print(addelection_form.errors)
    else:
        addelection_form=Electionform()

    return render(request,'organiser_app/election_form.html',{'addelection_form':addelection_form })

@login_required
def candidate_view(request,pk):
    template_name='organiser_app/candidate_detail.html'
    candidate=get_object_or_404(Candidate,pk=pk)
    region=region_options[candidate.candidate_region]
    context={'object':candidate, 'region':region}
    return render(request,template_name,context=context)

@login_required
def candidate_update(request,pk):
    template_name='organiser_app/candidate_form.html'
    candidate=get_object_or_404(Candidate,pk=pk)
    form=Candidateform(request.POST or None,instance=candidate)
    if request.method=="POST":

        if form.is_valid():
            form.save()
            #return HttpResponseRedirect(reverse( organiser_app:candidate_edit 'form.candidate_id ))

    return render(request,template_name,{'form':form})
@login_required
def reg_candidate(request,pk):
    template_name='organiser_app/region_candidate.html'
    candidates=Candidate.objects.filter(candidate_region=pk)

    context={'candidates':candidates}
    return render(request,template_name,context)

@login_required
def party_candidate(request,pk):
    template_name='organiser_app/region_candidate.html'
    candidates=Candidate.objects.filter(candidate_party=pk)
    context={'candidates':candidates}
    return render(request,template_name,context)


@login_required
def election_candidate(request,pk):
    template_name='organiser_app/region_candidate.html'
    candidates_ele=Candidate_election.objects.filter(election=pk)
    list_candidate=[]
    for candi in candidates_ele:
        list_candidate.append(candi.candidate)
    context={'candidates':list_candidate}
    return render(request,template_name,context)

@login_required
def candidate_election(request,pk):
    template_name='organiser_app/election.html'
    election_ins=Candidate_election.objects.filter(candidate=pk)
    election_instance=[]
    for ele in election_ins:
        election_instance.append(ele.election)
    context={'election_instance':election_instance}
    return render(request,template_name,context)

@login_required
def election_update(request,pk):
    template_name='organiser_app/election_update.html'
    election=get_object_or_404(Election,pk=pk)
    form=Electionform(request.POST or None,instance=election)
    if request.method=="POST":
        if form.is_valid():
            election_instance=form.save()
            id=election_instance.election_id
            for candi in Candidate_election.objects.filter(election=id):
                candi.delete()

            for candidate in election_instance.candidates.all():

                candidate_election_instance = Candidate_election()
                candidate_election_instance.candidate = candidate
                candidate_election_instance.election = election_instance
                candidate_election_instance.save()

            for reg in Election_region.objects.filter(election=id):
                reg.delete()

            if election_instance.election_type == 'P':
                for i in range(0,10):
                    election_region_instance=Election_region()
                    election_region_instance.region=i
                    election_region_instance.election=election_instance
                    election_region_instance.save()

            if election_instance.election_type=='A':
                election_region_instance=Election_region()
                region=request.POST['statelist']
                election_region_instance.region=region
                election_region_instance.election=election_instance
                election_region_instance.save()

            election_instance=Election.objects.all()
            context={'election_instance':election_instance}
            return render(request,'organiser_app/election.html',context)

    return render(request,template_name,{'form':form})



class candidateListView(APIView):

    def get(self,request):
        candidate=Candidate.objects.all()
        serializer=CandidateSerializer(candidate,many=True)
        return Response(serializer.data)

"""
def job():
    date=datetime.date.today()
    elections=Election.objects.all()
    for election in elections:
        if date <= election.date_of_start:
            print('hiii')
            election.status = '0'
        if date >= election.date_of_start and date <= election.date_of_end:
            election.status = '1'
        if date >= election.date_of_end:
            election.status = '2'

        election.save()


schedule.every(6).hours.do(job)

while 1:
    schedule.run_pending()
    time.sleep(1)
"""
