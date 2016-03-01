Rails.application.routes.draw do

  mount RailsAdmin::Engine => '/admin', as: 'rails_admin'
  get 'rooms/index'

  get 'schedules/index'

  devise_for :users, :controllers => { :omniauth_callbacks => "users/omniauth_callbacks" }

  root 'homes#index'
  resources :students
  resources :demographics
  resources :homes
  resources :schedules
  resources :rooms

  resources :photos, only: [:index, :show, :new, :create, :destroy]

end
