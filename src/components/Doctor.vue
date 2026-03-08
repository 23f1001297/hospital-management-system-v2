<template>
    <div>
        <div class="d-flex justify-content-between align-items-center bg-dark text-white">
            <h3 class="mb-0">Hospital Management System | Doctor </h3>
            <div>
                <span class="me-3">Welcome,  <strong>{{ doctorName }}</strong></span>
                <button @click="view = 'profile'" class="btn btn-primary btn-sm me-2" v-if="view !== 'profile'">Profile</button>
                <button v-else @click="view = 'dash'" class="btn btn-info btn-sm me-2">Dashboard</button>
                <button @click="logout" class="btn btn-warning btn-sm">Logout</button>
            </div>
        </div>
        <div class="container mt-4">
            <div v-if="view === 'profile'">
                <Profile :userId="doctorId "/>
            </div>
        </div>
        <div v-if="appointments.length === 0" class="alert alert-info">No appointments assigned. </div>
        <div v-for="a in appointments" :key="a.id" class="card mb-3 shadow-sm">
            <div class="card-body">
                <h5 class="card-title">{{ a.patient }}</h5>
                <p class="card-text">
                    <b>Date:</b> {{ a.date }} <br />
                    <b>Time:</b> {{ a.time }} <br />
                    <b>Status:</b>
                    <span class="badge bg-warning" v-if="a.status === 'Booked'">Booked</span>
                    <span class="badge bg-success" v-if="a.status === 'Completed'">Completed</span>
                    <span class="badge bg-danger" v-if="a.status === 'Cancelled'">Cancelled</span>
                </p>
                <div v-if="a.status === 'Booked'" class="mt-3">
                    <h5 class="mb-3">Treatment Details</h5>
                    <div class="mb-3">
                        <label class="form-label">Diagnosis:</label>
                        <input type="text" class="form-control mb-2" v-model="form[a.id].diagnosis">
                    </div>
                    <br>
                    <div class="mb-3">
                        <label class="form-label">Prescription:</label>
                        <input type="text" class="form-control mb-2" v-model="form[a.id].prescription">
                    </div>
                    <br>
                    <div class="mb-4">
                        <label class="form-label">Notes:</label>
                        <textarea class="form-control mb-4" v-model="form[a.id].notes"></textarea>
                    </div>
                    <br>
                    <div class="d-flex gap-2">
                        <button class="btn btn-success btn-sm me-2" @click="complete(a.id)">Complete</button>
                        <button class="btn btn-danger btn-sm" @click="cancel(a.id)">Cancel</button>
                    </div>
                </div>
                <br>
                <button class="btn btn-info btn-sm mt-2" @click="loadHistory(a.patient_id)">Patient history </button>
            </div>
        </div><hr v-if="his.length">
        <div v-if="his.length" class="mt-4 p-3 bg-light borderd rounded">
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="mb-0">Patient History</h5>
            </div>
            <ul class="lit-group">
                <li v-for="h in his" :key="h.date" class="list-group-item shadow-sm">
                    <span class="badge bg-secondary">{{ h.date }}</span> <br>
                    <b>Diagnosis:</b> {{ h.diagnosis }}<br>
                    <b>Prescription:</b> {{ h.prescription }}<br>
                    <b>Notes:</b> {{ h.notes }}
                </li>
            </ul>
        </div>

    </div>
</template>
<script>
import axios from 'axios';
import Profile from './Profile.vue';
export default{
    props: ['doctorId', 'doctorName'],
    components:{Profile},
    data(){
        return {
            view: 'dash',
            appointments: [],
            form:{},
            his: []
        };
    },
    
    mounted(){
        console.log("Doctor ID:", this.doctorId)
        this.loadAppointments();
    },
    methods:{
        loadAppointments(){
            axios.get(`/doctor/appointments/${this.doctorId}`)
            .then((res) => {
                this.appointments = res.data;
                res.data.forEach((a) => {
                    if (!this.form[a.id]){
                        this.form[a.id] = {
                            diagnosis: "",
                            prescription: "",
                            notes: ""
                        };
                    }
                });
            });
        },
        loadHistory(patientId){
            this.his = [];
            axios.get(`/doctor/phist/${patientId}/${this.doctorId}`)
            .then(res => {
                this.his = res.data;
            })
            .catch(err => {
                console.error("Error fetching hisory:", err);
            });
        },
        complete(apptId){
            const data = this.form[apptId]
            if(!data.diagnosis || !data.prescription){
                alert("Please enter diagnosis and prescription");
                return;
            }
            axios.post(`/doctor/complete/${apptId}`, data)
            .then(() => {
                alert("Appointment completed");
                this.loadAppointments();
            })
            .catch(() => {
                alert("Failed to complete appointment");
            });
        },
        cancel(apptId){
            axios.put(`/doctor/cancel/${apptId}`)
            .then(() => {
                alert("Appointment cancelled");
                this.loadAppointments();
            })
            .catch(() => {
                alert("Failed to cancel appointment");
            });
        },
        logout(){
            this.$emit('logout')
        }
    }
};
</script>
<style scoped>
.card{
    border-radius: 10px;
}
</style>
