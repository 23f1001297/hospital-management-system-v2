<template>
    <div>
        <div class="d-flex justify-content-between align-items-center bg-dark text-white">
            <h3 class="mb-0">Hospital Management System | Patient </h3>
            <div>
                <span class="me-3">Welcome, <strong>{{ patientName }}</strong></span>
                <button @click="view = 'profile'" class="btn btn-primary btn-sm me-2" v-if="view !== 'profile'">Profile</button>
                <button v-else @click="view = 'dash'" class="btn btn-info btn-sm me-2">Dashboard</button>
                <button @click="logout" class="btn btn-warning btn-sm">Logout</button>
            </div>
        </div>
        <div class="container mt-4">
            <div v-if="view === 'profile'">
                <Profile :userId="patientId "/>
            </div>
        </div>
        <div class="container mt-4">
            <div class="card mb-4 shadow-sm">
                <div class="card-body">
                    <h5>Available Doctors</h5>
                    <div class="row mb-4">
                        <div class="col-md-4" v-for="d in doctors" :key="d.id">
                            <h5>{{ d.name }}</h5>
                            <p>
                                <b>Specialization:</b> {{ d.special }}<br>
                                <b>Available:</b> {{ d.availability }}<br>
                            </p>
                        </div>
                    </div>
                    <h5>Book Appointments</h5>
                    <select v-model="booking.doctor_id" class="form-select mb-2" @change="chooseDoctor">
                        <option disabled value="">Select Doctor</option>
                        <option v-for="d in doctors" :key="d.id" :value="d.id">{{ d.name }} - {{ d.special }}</option>
                    </select>
                    <div v-if="selectDoctor" class="alert alert-info">
                        <b>Specialization:</b> {{ selectDoctor.special }} <br>
                        <b>availability:</b> {{ selectDoctor.availability }}
                    </div>
                    <input type="date" v-model="booking.date" class="form-control mb-2">
                    <input type="time" v-model="booking.time" class="form-control mb-2">
                    <button class="btn btn-success" @click="book">Book Appointment</button>
                </div>
            </div>
            <h5>My Appointment</h5>
            <div v-if="appointments.length === 0" class="alert alert-info">No Appointments</div>
            <div v-for="a in appointments" :key="a.id" class="card mb-3 shadow-sm">
                <div class="card-body">
                    <h6>{{ a.doctor }}</h6>
                    <p>
                        Date: {{ a.date }}<br>
                        Time: {{ a.time }}<br>
                        <span class="badge bg-warning" v-if="a.status==='Booked'">Booked</span>
                        <span class="badge bg-success" v-if="a.status==='Completed'">Completed</span>
                        <span class="badge bg-danger" v-if="a.status==='Cancelled'">Cancelled</span>
                    </p>
                    <button v-if="a.status==='Booked'" class="btn btn-danger" @click="cancels(a.id)">Cancel</button>
                </div>
            </div>
            <div v-if="history.length" class="mt-4">
                <h4>Medical History</h4>
                <div v-for="h in history" :key="h.date" class="card mb-3 shadow-sm">
                    <div class="card-body">
                        <h5>{{ h.date }}</h5>
                        <p>
                            <b>Doctor:</b> {{ h.doctor }}<br>
                            <b>Diagnosis:</b> {{ h.diagnosis }}<br>
                            <b>Prescription:</b> {{ h.prescription }}<br>
                            <b>Notes:</b> {{ h.notes }}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import axios from 'axios';
import Profile from './Profile.vue';
export default{
    props: ['patientId', 'patientName'],
    components:{Profile},
    data() {
        return{
             view: 'dash',
            doctors: [],
            appointments: [],
            history: [],
            selectDoctor: null,
            booking:{
                doctor_id: "",
                date: "",
                time: ""
            }
        };
    },
    mounted(){
        this.loadDoctors();
        this.loadHistory();
        this.loadAppointments();
    },
    methods:{
        loadDoctors(){
            axios.get('/patient/docs')
            .then(res => {
                this.doctors = res.data;
            });
        },
        loadAppointments(){
            axios.get(`/patient/appo/${this.patientId}`)
            .then(res => {
                this.appointments = res.data;
            });
        },
        loadHistory(){
            axios.get(`/patient/history/${this.patientId}`)
            .then(res => {
                this.history = res.data;
            });
        },
        chooseDoctor(){
            this.selectDoctor = this.doctors.find(
                d => d.id === Number(this.booking.doctor_id)
            );
        },
        book(){
            if(!this.booking.doctor_id || !this.booking.date || !this.booking.time){
                alert("Fill all fields");
                return;
            }
            axios.post('/patient/book', {
                patient_id: this.patientId,
                doctor_id: this.booking.doctor_id,
                date: this.booking.date,
                time: this.booking.time
            }).then(() => {
                alert("Appointment booked");
                this.booking = {
                    doctor_id: "",
                    date: "",
                    time: ""
                };
                this.loadAppointments();
            });
        },
        cancels(id){
            axios.put(`/patient/cancels/${id}`)
            .then(() => {
                alert("Cancelled");
                this.loadAppointments();
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

