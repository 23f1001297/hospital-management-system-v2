<template>
  <div>
    <div v-if="!currentUser" class="row justify-content-center">
      <div class="col-md-5">
        <div class="card shadow border-0">
          <div  class="card-body p-4">
            <h2 class="text-center mb-4">{{ isLogin ? 'Login' : 'Register' }}</h2>
            <hr>
            <div class="mb-3">
              <label class="form-label">Username</label>
              <input v-model="form.username" type="text" class="form-control">
            </div>
            <div v-if="!isLogin" class="mb-3">
              <label class="form-label">Name</label>
              <input v-model="form.name" type="text" class="form-control">
            </div>
            <div class="mb-3">
              <label class="form-label">Password</label>
              <input v-model="form.password" type="password" class="form-control">
            </div>
            <button @click="handleAuth" class="btn btn-info w-100 py-2">
              {{  isLogin ? 'Sign In' : 'Create Account'}}
            </button>
            <p class="text-center mt-3">
              <a href="#" @click="isLogin = !isLogin" class="text-decoration-none">
                {{ isLogin ? "New patient? Register here": "Already have an account? Login" }}
              </a> 
            </p>
          </div>
        </div>
      </div>
    </div>
    <div v-else>
      <Admin v-if="currentUser.role === 'admin'" :adminName="currentUser.name" @logout="logout"/>
      <Doctor v-else-if="currentUser.role === 'doctor'" :doctorId="currentUser.id" :doctorName="currentUser.name" @logout="logout"/>
      <Patient v-else-if="currentUser.role === 'patient'" :patientId="currentUser.id" :patientName="currentUser.name" @logout="logout"/>
    </div>
  </div>
</template>
<script>
import axios from 'axios'
import Admin from './components/Admin.vue'
import Doctor from './components/Doctor.vue'
import Patient from './components/Patient.vue'
axios.defaults.baseURL = "http://localhost:5000";
export default{
  components: {
    Admin,
    Doctor,
    Patient
  },
  data(){
    return{
      isLogin: true,
      currentUser: null,
      form:{
        username: '',
        password: '',
        name: ''
      }
    }
  },
  methods: {
    async handleAuth(){
      const path = this.isLogin ? '/login' : '/register';
      try {
        const response = await axios.post(path, this.form);
        if (this.isLogin){
          this.currentUser = response.data;
          alert("Login successful");
        }else{
          alert("Registration successful . Please login.");
          this.isLogin = true;
          this.form.password = '';
        }
      }catch(error){
        console.log(error);
        alert("Error: Server connection failed");
      }
    },
    logout(){
      this.currentUser = null;
      this.form = {
        username: '',
        password: '', 
        name: ''
      };
    }
  }
}
</script>