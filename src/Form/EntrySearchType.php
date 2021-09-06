<?php

namespace App\Form;

use App\Entity\User;
use Symfony\Bridge\Doctrine\Form\Type\EntityType;
use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\Extension\Core\Type\DateType;
use Symfony\Component\Form\Extension\Core\Type\TextType;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\OptionsResolver\OptionsResolver;

class EntrySearchType extends AbstractType
{
    public function buildForm(FormBuilderInterface $builder, array $options)
    {
        $builder
            ->add("userEquals", EntityType::class, [
                "required" => false,
                "class" => User::class,
            ])
            ->add("categoryContains", TextType::class, [
                "required" => false
            ])
            ->add("payeeContains", TextType::class, [
                "required" => false
            ])
            ->add("notesContains", TextType::class, [
                "required" => false
            ])
            ->add("dateFrom", DateType::class, [
                "required" => false,
                "widget" => "single_text",
                "html5" => true
            ])
            ->add("dateTo", DateType::class, [
                "required" => false,
                "widget" => "single_text",
                "html5" => true
            ])
        ;
    }

    public function configureOptions(OptionsResolver $resolver)
    {
        $resolver->setDefaults([
            // Configure your form options here
        ]);
    }
}
