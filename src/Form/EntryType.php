<?php

namespace App\Form;

use App\Entity\Entry;
use Symfony\Component\Form\AbstractType;
use Symfony\Component\Form\Extension\Core\Type\DateType;
use Symfony\Component\Form\FormBuilderInterface;
use Symfony\Component\OptionsResolver\OptionsResolver;

class EntryType extends AbstractType
{
    public function buildForm(FormBuilderInterface $builder, array $options)
    {
        $builder
            ->add("entryDate", DateType::class, [
                "required" => true,
                "widget" => "single_text",
                "input" => "datetime_immutable",
                "html5" => true
            ])
            ->add("price", null, [
                "required" => true,
                "html5" => true,
                "scale" => 2,
                "attr" => [
                    "step" => 0.01
                ]
            ])
            ->add("payee")
            ->add("category")
            ->add("notes")
        ;
    }

    public function configureOptions(OptionsResolver $resolver)
    {
        $resolver->setDefaults([
            "data_class" => Entry::class,
        ]);
    }
}
