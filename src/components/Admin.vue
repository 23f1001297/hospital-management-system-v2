<template>
    <div>
        <div class="d-flex justify-content-between align-items-center bg-dark text-white px-4 py-3 shadow">
            <h1 class="mb-0">Hospital Management System | Admin </h1>
            <div>
                <span class="me-3">
                    Welcome,   <strong>{{  adminName }}</strong>
                </span>
                <button @click="logout" class="btn btn-warning btn-sm">Logout</button>
            </div>
        </div>
        <div class="container mt-4">
            <div class="d-flex justify-content-between mb-4">
                <input v-model="search" class="form-control w-50">
                <button class="btn btn-info ms-2">Search</button>
            </div>
            <div class="card shadow mb-4">
                <div class="card-header bg-light">Registered Doctors</div>
                <div class="card-body">
                    <div v-for="doc in filteredDoctors" :key="doc.id" class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>{{ doc.name }}<span v-if="doc.blacklist" class="text-danger">(Blocked)</span></strong>
                            <small class="text-muted">({{ doc.special }})</small>
                        </div>
                        <div>
                            <button class="btn btn-sm btn-info" @click="editDoctor(doc)">Edit</button>
                            <button @click="deleteDoctor(doc.id)"class="btn btn-sm btn-danger">Delete</button>
                            <button @click="toggleBlacklist(doc.id)" class="btn btn-sm btn-secondary" >{{ doc.blacklist ? 'Unblock' : 'Blacklist' }}</button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="card shadow mb-4">
                <div class="card-header bg-light">Registered Patients</div>
                <div class="card-body">
                    <div v-for="pat in filteredPatients" :key="pat.id" class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>{{ pat.name }}<span v-if="pat.blacklist" class="text-danger">(Blocked)</span></strong>
                        </div>
                        <div>
                            <button class="btn btn-sm btn-info" @click="startEditPatient(pat)">Edit</button>
                            <button @click="deletePatient(pat.id)"class="btn btn-sm btn-danger">Delete</button>
                            <button @click="toggleBlacklist(pat.id)" class="btn btn-sm btn-secondary" >{{ pat.blacklist ? 'Unblock' : 'Blacklist' }}</button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="card shadow mb-4">
                <div class="card-header bg-light">Upcoming Appointments</div>
                <div class="card-body table-responsive">
                    <table class="table table-bordered text-center">
                        <thead class="table-light">
                            <tr>
                                <th>Sr No.</th>
                                <th>Patient</th>
                                <th>Doctor</th>
                                <th>Date</th>
                                <th>Time</th>
                                <th>Status</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(appt,index) in appointments" :key="appt.id">
                                <td>{{ index + 1 }}</td>
                                <td>{{ appt.patient_name }}</td>
                                <td>{{ appt.doctor_name }}</td>
                                <td>{{ appt.date }}</td>
                                <td>{{ appt.time }}</td>
                                <td>
                                    <span class="badge bg-warning" v-if="appt.status=='Pending'">Pending</span>
                                    <span class="badge bg-success" v-if="appt.status=='Approved'">Approved</span>
                                    <span class="badge bg-info" v-if="appt.status=='Completed'">Completed</span>
                                </td>
                                <td><button @click="deleteAppointment(appt.id)" class="btn btn-sm btn-danger">Delete</button></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <div class="card shadow mb-5">
                <div class="card-header bg-light">Add Doctors</div>
                <div class="card-body">
                    <div class="row mb-3">
                        <label class="col-sm-4 col-form-label">Username:</label>
                        <div class="col-md-6">
                        <input type="text" v-model="form.username" class="form-control" :disabled="editMode">
                        </div>
                    </div>
                    <div class="row mb-3">
                        <label class="col-sm-4 col-form-label">Password:</label>
                        <div class="col-md-6">
                        <input type="password" v-model="form.password" class="form-control" :disabled="editMode">
                        </div>
                    </div>
                    <div class="row mb-3">
                        <label class="col-sm-4 col-form-label">Name:</label>
                        <div class="col-md-6">
                        <input type="text" v-model="form.name" class="form-control">
                        </div>
                    </div>
                    <div class="row mb-3">
                        <label class="col-sm-4 col-form-label">Specialization:</label>
                        <div class="col-md-6">
                        <input type="text" v-model="form.special" class="form-control">
                        </div>
                    </div>
                    <div class="row mb-3">
                        <label class="col-sm-4 col-form-label">Start time:</label>
                        <div class="col-md-6">
                        <input type="time" v-model="form.startTime" class="form-control">
                        </div>
                    </div>
                    <div class="row mb-3">
                        <label class="col-sm-4 col-form-label">End time:</label>
                        <div class="col-md-6">
                        <input type="time" v-model="form.endTime" class="form-control">
                        </div>
                    </div>
                    <button @click="editMode ? submitEdit() : addDoc()" class="btn btn-warning w-100">{{ editMode ? "Update" : "Add Doc + " }}</button>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import axios from 'axios'
export default{
    props: ['adminName'],
    data(){
        return{
            search:'',
            doctors:[],
            patients:[],
            appointments:[],
            editMode:false,
            editId:null,
            editType:null,
            form:{
                username:'',
                password:'',
                name:'',
                special:'',
                startTime:'',
                endTime:''
            }
        }
    },
    computed:{
        filteredDoctors(){
            return this.doctors.filter(d=> d.name.toLowerCase().includes(this.search.toLowerCase()))
        },
        filteredPatients(){
            return this.patients.filter(p=> p.name.toLowerCase().includes(this.search.toLowerCase()))
        }
    },
    mounted(){
        this.loadAll()
    },
    methods:{
        async loadAll(){
            const doc = await axios.get('/docs')
            const pat = await axios.get('/patient')
            const appt = await axios.get('/appoints')
            this.doctors = doc.data
            this.patients = pat.data
            this.appointments = appt.data
        },
        editDoctor(doc){
            this.editMode = true
            this.editId = doc.id
            this.editType = 'doctor'
            this.form.name = doc.name
            this.form.special = doc.special
            if(doc.availability){
                const times = doc.availability.split(" - ")
                this.form.startTime = times[0]
                this.form.endTime = times[1]
            }
        },
        async searchUsers(){
            const res = await axios.get(`/search?type=doctor&q=${this.search}`)
            this.doctors = res.data
        },
        async toggleBlacklist(id){
            await axios.put(`/blacklist/${id}`)
            this.loadAll()
        },
        startEditPatient(pat){
            this.editMode = true
            this.editId  = pat.id
            this.form.name = pat.name
            this.editType = 'patient'
        },
        async deletePatient(id){
            await axios.delete(`/delete_p/${id}`)
            this.loadAll()
        },
        async deleteAppointment(id){
            await axios.delete(`/delete_ap/${id}`)
            this.loadAll()
        },
        resetForm(){
            this.form = {
                username:'',
                password:'',
                name:'',
                special:'',
                startTime:'',
                endTime:''
            }
        },
        async addDoc(){
            try{
                console.log("Add doctor button clicked")
                const avail = this.form.startTime + " - " + this.form.endTime
                await axios.post('/add_doc',{
                    username: this.form.username,
                    password:this.form.password,
                    name:this.form.name,
                    special:this.form.special,
                    availability:avail
                })
                alert("Doctor added")
                this.resetForm()
                this.loadAll()
            }catch(err){
                console.log(err)
                alert("Failed to add doctor")
            }
           
        },
        async submitEdit(){
            try{
                if(this.editType === 'doctor'){
                    const avail = this.form.startTime + " - " + this.form.endTime
                    await axios.put(`/edit_doc/${this.editId}`,{
                        name:this.form.name,
                        special:this.form.special,
                        availability:avail
                    })
                    alert("Doctor updated")
                }
                else if(this.editType === 'patient'){
                    await axios.put(`/edit_patient/${this.editId}`,{
                        name:this.form.name
                    })
                    alert("Patient updated")
                }
                this.editMode = false,
                this.editId = null,
                this.editType = null,
                this.resetForm()
                this.loadAll()
            }catch(err){
                console.log(err)
                alert("Update failed")
            }
        },
        async deleteDoctor(id){
            await axios.delete(`/delete_doc/${id}`)
            this.loadAll()
        },
        logout(){
            this.resetForm()
            this.$emit('logout')
        }
    }
}
</script>