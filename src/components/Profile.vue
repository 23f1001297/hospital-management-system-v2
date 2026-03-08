<template>
    <div class="card shadow-sm p-4">
        <h3>Edit Profile</h3>
        <hr>
        <div class="row">
            <div class="col-md-6 mb-3">
                <label>Username</label>
                <input type="text" class="form-control" v-model="user.username" disabled>
            </div>
            <div class="col-md-6 mb-3">
                <label>Name</label>
                <input type="text" class="form-control" v-model="user.name">
            </div>
            <div class="col-md-6 mb-3">
                <label>Mobile No.</label>
                <input type="text" class="form-control" v-model="user.mobile">
            </div>
            <div class="col-md-6 mb-3">
                <label>Age</label>
                <input type="text" class="form-control" v-model="user.age">
            </div>
            <div class="col-md-6 mb-3">
                <label>Gender</label>
                <select class="form-select" v-model="user.gender">
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                </select>
            </div>
            <div class="col-12 mb-3">
                <label>Address</label>
                <textarea class="form-control" v-model="user.address"></textarea>
            </div>
        </div>
        <button class="btn btn-info" @click="saveprofile">Save</button>
    </div>
</template>
<script>
import axios from 'axios';
export default{
    props: ['userId'],
    data(){
        return {user: {}};
    },
    mounted(){
        this.fetchProfile();
    },
    methods:{
        fetchProfile(){
            axios.get(`/profile/${this.userId}`).then(res => this.user = res.data);
        },
        saveprofile(){
            axios.put(`/profile/update/${this.userId}`, this.user)
            .then(() => alert("Profile updated"));
        },
    }
}
</script>

